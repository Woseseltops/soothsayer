import os;
import subprocess;
import sys;
import time;
import multiprocessing;
import math;

############### Functions ###################################

def command(command,piped = False):

    if piped:
        result = subprocess.Popen(command, shell=True,stdout=subprocess.PIPE).communicate()[0].decode();
    else:
        f = open('TiMBL_output','w');
        result = subprocess.Popen(command, shell=True,stdout=f,stderr=f);
        result.wait();

    return(result);

def get_character_function():
    """Return a function which gets a single char from the input"""

    try:
        #Windows variant

        import msvcrt

        def function():
            import msvcrt
            return msvcrt.getch().decode()

    except ImportError:
        #Unix variant

        def function():
            import sys, tty, termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch            

    return function;        

def clear():
    """Clears the screen""";

    os.system(['clear','cls'][os.name == 'nt']);

def do_prediction(text,model,lexicon,approach,cut_off_lexicon):
    """Returns a prediction by TiMBL and related info""";

    words = text.split();

    if approach == 'w':

        if text == '' or text[-1] == ' ':

            #Figure out the left context and the word being worked on
            current_word = '';
            words = words[-3:]

            #Make ready for Timbl
            while len(words) < 3:
                words = ['_'] + words;


            lcontext = attenuate_string_simple(' '.join(words) + ' _',lexicon);
            open('predictions/lcontext','w').write(lcontext);

            #Ask TiMBL for new prediction
            command('timbl -t predictions/lcontext -i '+model+'.training.txt.IGTree +vdb +D -a1 -G +vcf');

        else:
            current_word = words[-1];
            words = words[-4:-1];
    elif approach == 'l':

        #Figure out the left context and the word being worked on
        lcontext = ' '.join(text[-15:].replace(' ','_')) + ' ?';

        #Make ready for TiMBL
        while len(lcontext) < 30:
            lcontext = '_ ' + lcontext;

        open('predictions/lcontext','w').write(lcontext);
        if text == '' or text[-1] == ' ':
            current_word = '';
        else:
            current_word = words[-1];

        #Ask TiMBL for new prediction
        command('timbl -t predictions/lcontext -i '+model+' +vdb +D -a1 -G +vcf');

    #Turn prediction into list of tuples
    raw_distr = open('predictions/lcontext.IGTree.gr.out','r').read().split('] {');
    raw_distr = raw_distr[1];
    distr = raw_distr.strip()[:-2].split();

    last_word = None;
    predictions = [];
    for i in distr:

        if last_word == None:
            last_word = i;
        else:
            predictions.append((last_word,float(i[:-1])));
            last_word = None;

    #Pick the best prediction, based on what has been typed so far
    boundary = len(current_word);

    pick = '';
    highest_confidence = 0;

    second_pick = '';
    second_highest_confidence = 0;

    third_pick = '';
    third_highest_confidence = 0;

    for i in predictions:
        if i[0] != '#DUMMY' and (i[0][:boundary] == current_word or approach == 'l'):
            if i[1] > highest_confidence:
                third_pick = second_pick;
                third_highest_confidence = second_highest_confidence;

                second_pick = pick;
                second_highest_confidence = highest_confidence;
                
                pick = i[0];
                highest_confidence = i[1];
            elif i[1] > second_highest_confidence:
                third_pick = second_pick;
                third_highest_confidence = second_highest_confidence;

                second_pick = i[0];
                second_highest_confidence = i[1];                
            elif i[1] > third_highest_confidence:
                third_pick = i[0];
                third_highest_confidence = i[1];

    source = 'IGTREE';

    #Nothing found? Use lexicon as safety net
    if pick == '':
        lexicon = open(model+'.lex.txt');
        
        for i in lexicon:
            word, freq = i.split();
            if word[:boundary] == current_word:
                pick = word;
                source = 'LEXICON';
                break;
            elif int(freq) < cut_off_lexicon:
                break;
    
    return {'full_word':pick,'word_so_far':current_word,'nr_options':len(predictions),
            'second_guess':second_pick,'third_guess':third_pick, 'source': source}; 

def add_prediction(text,prediction):

    if text[-1] == ' ':
        return text + prediction + ' ', '';
    else:
        words = text.split();
        last_input = words[-1];
        words = words[:-1];
        words.append(prediction);
        return ' '.join(words) + ' ', last_input;
    
def demo_mode(model,lexicon,approach,cut_off_lexicon):
    print('Start typing whenever you want');

    #Predict starting word
    prediction = do_prediction('',model,lexicon,approach,cut_off_lexicon);

    #Ask for first char    
    get_character = get_character_function();

    #Start the process
    busy = True;
    text_so_far = '';

    while busy:
        char = str(get_character());

        #Accept prediction
        if char == ' ':
            if prediction['full_word'] != '':
                text_so_far, last_input = add_prediction(text_so_far,prediction['full_word']);
            else:
                text_so_far += ' ';

        #Reject prediction
        elif char == '\t':
            text_so_far+= ' ';

        #Don't accept prediction
        else:
            text_so_far += char;

        #Predict new word
        prediction = do_prediction(text_so_far,model,lexicon,approach,cut_off_lexicon);

        #Show the prediction
        clear();

        chars_typed = len(prediction['word_so_far']);
        print(text_so_far+'|'+prediction['full_word'][chars_typed:]);
        print();
        print(prediction['second_guess']+', '+prediction['third_guess']+', '+ \
              str(prediction['nr_options'])+' options, source:',prediction['source']);

        if prediction['full_word'] == '':
            print('Switch to word list');

        #Check for quit
        if 'quit' in text_so_far.split():
            busy = False;

def simulation_mode(model,lexicon,testfile,approach,cut_of_lexicon):

    #Prepare vars and output
    starttime = time.time();
    teststring = open(testfile,'r').read();
    total_keystrokes_saved = 0;
    total_keystrokes_saved_sk = 0; #Swiftkey measure
    already_predicted = False;
    skks_got_it_already = False;

    open('Soothsayer_output','w');
    outputfile = open('Soothsayer_output','a');

    open('predictions_marked','w');
    predictions_marked_file = open('predictions_marked','a');

    #Go through the testfile letter for letter
    for i in range(len(teststring)):

        if teststring[i] == ' ':
            skks_got_it_already = False;

        #If the word was not already predicted, guess (again)
        if not already_predicted:

            #Do prediction and compare with what the user was actually writing
            text_so_far = teststring[:i];
            prediction = do_prediction(text_so_far,model,lexicon,approach,cut_off_lexicon);
            current_word = find_current_word(teststring,i);
            outputfile.write(prediction['word_so_far']+', '+ current_word+', '+prediction['full_word']+'\n');

            #If correct, calculate keystrokes saved and put in output
            if current_word == prediction['full_word']:
                outputfile.write('\n## FIRST GUESS CORRECT. SKIP. \n');
                predictions_marked_file.write('<');

                keystrokes_saved = calculate_keystrokes_saved(prediction['word_so_far'],current_word);
                    
                outputfile.write('## KEYSTROKES SAVED ' + str(keystrokes_saved)+' \n');

                total_keystrokes_saved += keystrokes_saved;
                perc = str(total_keystrokes_saved / len(text_so_far));
                outputfile.write('## CKS ' + str(total_keystrokes_saved) + ' of ' + str(len(text_so_far)) + ' (' +perc+'%) \n');

                if not skks_got_it_already:
                    total_keystrokes_saved_sk += keystrokes_saved;            
                    perc = str(total_keystrokes_saved_sk / len(text_so_far));
                    outputfile.write('## SKKS ' + str(total_keystrokes_saved_sk) + ' of ' + str(len(text_so_far)) + ' (' +perc+'%) \n');

                outputfile.write('## DURATION: '+str(time.time() - starttime)+' seconds \n\n');

                if teststring[i] != ' ':
                    already_predicted = True;

            elif current_word == prediction['second_guess']:
                outputfile.write('\n## SECOND GUESS CORRECT \n');

                keystrokes_saved = calculate_keystrokes_saved(prediction['word_so_far'],prediction['second_guess']);

                total_keystrokes_saved_sk += keystrokes_saved;            

                perc = str(total_keystrokes_saved_sk / len(text_so_far));
                outputfile.write('## SKKS ' + str(total_keystrokes_saved_sk) + ' of ' + str(len(text_so_far)) + ' (' +perc+'%) \n\n');

                skks_got_it_already = True;

            elif teststring[i-1] == ' ' and current_word == prediction['third_guess']:
                outputfile.write('\n## THIRD GUESS CORRECT \n');

                keystrokes_saved = calculate_keystrokes_saved(prediction['word_so_far'],prediction['third_guess']);

                total_keystrokes_saved_sk += keystrokes_saved;            

                perc = str(total_keystrokes_saved_sk / len(text_so_far));
                outputfile.write('## SKKS ' + str(total_keystrokes_saved_sk) + ' of ' + str(len(text_so_far)) + ' (' +perc+'%) \n\n');

                skks_got_it_already = True;
                
        #Skip if the word was already predicted
        else:
            if teststring[i] == ' ':
                already_predicted = False;

        predictions_marked_file.write(teststring[i]);                

def find_current_word(string, position):
    """Returns which word the user was typing at this position""";

    try:
        word = string[position-1];
    except IndexError:
        return '';

    separators = [' ','_'];

    #If starting with a space, give the next word
    while word in separators:
        position += 1;
        word = string[position-1];

    c = 2;
    while word[0] not in separators:
        word = string[position-c] + word;
        c += 1;

    c = 0;
    while word[-1] not in separators:
        try:
            word +=  string[position+c];
        except IndexError:
            break;
        c += 1;

    return word.strip();

def prepare_training_data(directory,mode,approach):

    if approach == 'w':
        foldername = 'wordmodels';
    elif approach == 'l':
        foldername = 'lettermodels';

    #Paste all texts in the directory into one string
    print('  Grab all files');
    files = os.listdir(directory);
    total_text = '';

    for i in files:
        if approach == 'w' and i not in ['allmail']:
            print(directory,i);
            total_text += ' _ _ _ '+open(directory+i,'r',encoding='utf-8',errors='ignore').read();
        elif approach == 'l':
            total_text += ' ________________ '+open(directory+i,'r').read();

    #Create and load lexicon
    print('  Create lexicon');
    lexicon_filename = foldername+'/'+directory[:-1]+'.lex.txt'; 
    string_to_lexicon(total_text,lexicon_filename);
    lexicon = load_lexicon(lexicon_filename,att_threshold);

    #In simulation mode, cut away 10 percent for testing later
    print('  Make test file if needed');
    if mode == 's':
        testfilename = foldername+'/'+directory[:-1]+'.10.test.txt';
        training_filename = foldername+'/'+directory[:-1]+'.90.training.txt';

        words = total_text.split();
        boundary = round(len(words)*0.9);

        open(testfilename,'w').write(' '.join(words[boundary:]));
        total_text = ' '.join(words[:boundary]);

    #In demo mode, just take all
    else:
        testfilename = '';
        training_filename = foldername+'/'+directory[:-1]+'.training.txt';

    #Attenuate the string with the training text
    print('  Attenuate string');
    total_text = attenuate_string_multicore(total_text,lexicon);

    #Make into ngrams, and save the file
    print('  Make ngrams');
    ngrams = make_ngrams(total_text,approach);

    print('  Create file');
    training_file_content = '\n'.join(ngrams);
    open(training_filename,'w').write(training_file_content);

    #Return the filenames
    return training_filename, testfilename, lexicon;

def make_ngrams(text,approach):
    """Transforms a string into a list of 4-grams, using multiple cores""";

    result = multiprocessing.Queue();

    #Starts the workers
    def worker(nr,string,result):

        if approach == 'w':
            if nr == 0:
                ngrams = window_string(string,True);
            else:
                ngrams = window_string(string);
        elif approach == 'l':
            ngrams = window_string_letters(string);    

        result.put((nr,ngrams));

    substrings = divide_iterable(text.split(),10,3);
    
    for n,i in enumerate(substrings):
        t = multiprocessing.Process(target=worker,args=[n,i,result]);
        t.start();

    #Wait until all results are in
    resultlist = [];

    while len(resultlist) < 10:

        while not result.empty():
            resultlist.append(result.get());

        time.sleep(1);

    #Sort and merge the results
    resultlist = sorted(resultlist,key=lambda x:x[0]);
    between_result = [x[1] for x in resultlist];    
    end_result = [];
    for i in between_result:
        end_result += i;

    return end_result;
            
def window_string(string,verbose = False):
    """Return the string as a list of 4-grams""";

    if not isinstance(string,list):
        words = string.split();
    else:
        words = string;

    word_nr = len(words);
    ngrams = [];
    
    for n,i in enumerate(range(0,len(words)-3)):
        ngrams.append(' '.join(words[i:i+4]));

    #Remove useless ones
    ngrams_to_remove = [];
    for n,i in enumerate(ngrams):
        if i[-1] == '_':
            ngrams_to_remove.append(i);

#    if verbose:
#        print('Task 2/3 finished');

#    for i in ngrams_to_remove:
#        ngrams.remove(i);

#    if verbose:
#        print('Task 3/3 finished');

    return ngrams;

def window_string_letters(string):
    """Return the string as a list of letter 15-grams""";

    words = string.split();
    newstring = string.replace(' ','_').replace('\n','');
    ngrams = [];
    
    for i in range(0,len(string)+1):

        current_word = find_current_word(newstring, i).replace('_','');
        letters_before = ' '.join(newstring[i-15:i]);

        ngrams.append(letters_before + ' ' +current_word);

    #Remove useless ones
    ngrams_to_remove = [];
    for n,i in enumerate(ngrams):
        words = i.split();
        if i[-1] == '_' or len(words) != 16 or i == ngrams[-1]:
            ngrams_to_remove.append(i);

    for i in ngrams_to_remove:
        ngrams.remove(i);

    return ngrams[1:-1];

def train_model(filename):
    """Train a model on the basis of these ngrams""";

    command('timbl -f '+filename+' -I '+filename+'.IGTree +D +vdb -a1 -p 1000000',False);

    return filename.replace('.training.txt','');

def calculate_keystrokes_saved(word_so_far,prediction):

    keystrokes_saved = len(prediction) - len(word_so_far) - 1;

    if keystrokes_saved < 0:
        keystrokes_saved = 0;
    
    return keystrokes_saved;

def string_to_lexicon(string,outputfilename):
    """Creates a lexicon from a string""";

    #Counts words
    words = string.replace('\n','').split();
    counts = {};

    for i in words:
        try:
            counts[i] += 1;
        except KeyError:
            counts[i] = 1;

    #Sort words, most frequent first
    counts = sorted(list(counts.items()),key=lambda x: x[1],reverse=True);

    #Save results
    lines = '';

    for i in counts:
        lines += i[0] + ' ' +str(i[1]) + '\n';

    open(outputfilename,'w').write(lines);

def load_lexicon(filename,threshold):
    """Returns a list of all words more frequent than threshold""";

    lexicon = open(filename,'r');
    frequent_words = {};

    for i in lexicon:
        word,frequency = i.split();
        frequency = int(frequency);

        if frequency > threshold:
            try:
                frequent_words[len(word)].append(word);
            except KeyError:
                frequent_words[len(word)] = [word]

    return frequent_words;

def attenuate_string_simple(string,lex):
    """Replaces infrequent words in string with #DUMMY, using one core""";

    words = string.split();
    result = '';

    for i in words:
        try:
            if i not in lex[len(i)]:
                result += ' #DUMMY';
            else:
                result += ' ' + i;
        except KeyError:
            result += ' #DUMMY';

    return result.strip();

def attenuate_string_multicore(string,lex):
    """Replaces infrequent words in string with #DUMMY, using multiple cores""";

    #Prepare input and output
    words = string.split();
    word_nr = len(words);
    result = multiprocessing.Queue();

    #The actual work
    def dummify(n,word):        
        try:
            if not word in lex[len(word)] and word not in ['_']:
                return '#DUMMY';
            else:
                return word;

        except KeyError:
            return '#DUMMY';

    #Starts the workers
    def worker(nr,words,result):
        resultstring = '';
        wordtotal = len(words);

        for n,i in enumerate(words):
            
            resultstring += ' ' + dummify(n,i);

            #Report progress of the first worker
            if nr == 0 and n%100000 == 0:
                print('  ',n / wordtotal);

        result.put((nr,resultstring));

    substrings = divide_iterable(words,10);
    
    for n,i in enumerate(substrings):
        t = multiprocessing.Process(target=worker,args=[n,i,result]);
        t.start();

    #Wait until all results are in
    resultlist = [];

    while len(resultlist) < 10:

        while not result.empty():
            resultlist.append(result.get());

        time.sleep(1);

    #Sort and merge the results
    resultlist = sorted(resultlist,key=lambda x:x[0]);
    actual_result = [x[1] for x in resultlist];
        
    return ' '.join(actual_result).strip();

def attenuate_training_file(filename,lexicon):
    """Replaces infrequent words in trainingfile with #DUMMY""";

    f = open(filename,'r');

    newlines = [];
        
    for i in f:
        words = i.replace('\n','').split();
        result = '';
        
        for j in words[:-1]:
            if j not in lexicon and j not in ['_']:
                result += ' #DUMMY';
            else:
                result += ' '+j;

        result += ' '+words[-1];
        newlines.append(result.strip());

    open(filename,'w').write('\n'.join(newlines));

def divide_iterable(it,n,overlap=None):
    """Returns any iterable into n pieces""";

    save_it = it;
    piece_size = math.ceil(len(it) / n);
    result = [];
    while len(it) > 0:
        result.append(it[:piece_size]);
        it = it[piece_size:];

    #If not enough pieces, divide the last piece
    if len(result) != n:
        last_piece = result[-1];
        boundary = round(len(last_piece)/2);
        result.append(last_piece[boundary:]);
        result[-2] = last_piece[:boundary];

    #Add overlap if needed
    if overlap:
        for n,i in enumerate(result):

            #Add left overlap
            pos = piece_size * n;
            result[n] = save_it[pos-overlap:pos] + result[n];

    return result;

######### Script starts here######################

# Static settings
att_threshold = 10;
cut_off_lexicon = 3;

#Figure out settings
if '-d' in sys.argv:
    mode = 'd';
elif '-s' in sys.argv:
    mode = 's';
else:
    mode = input('Mode (d = demo, s = simulation): ');    

if '-l' in sys.argv:
    approach = 'l';
    modelfolder = 'lettermodels';
elif '-w' in sys.argv:
    approach = 'w';
    modelfolder = 'wordmodels';
else:
    approach = input('Approach (l = letter, w = word): ');

    if approach == 'l':
        modelfolder = 'lettermodels';
    elif approach == 'w':
        modelfolder = 'wordmodels';

if '-id' in sys.argv:
    for n,i in enumerate(sys.argv):
        if i == '-id':
            inp = sys.argv[n+1];
else:
    inp = input('Input directory (include (back)slash): ');

if '-tf' in sys.argv:
    for n,i in enumerate(sys.argv):
        if i == '-tf':
            testfile_preset = sys.argv[n+1];    
else:
    testfile_preset = False;

#Set directory reference (add .90 for the simulation mode)
if mode == 'd':
    dir_reference = inp[:-1];
elif mode == 's':
    dir_reference = inp[:-1] + '.90';

#Try opening the language model (and testfile), or create one if it doesn't exist
try:
    open(modelfolder+'/'+dir_reference+'.training.txt','r');
    print('Using existing model for '+dir_reference+'.');

    testfile = modelfolder+'/'+inp[:-1] + '.10.test.txt';
    model = modelfolder+'/'+dir_reference;
    lexicon = load_lexicon(modelfolder+'/'+inp[:-1]+'.lex.txt',att_threshold);
except IOError:
    print('Model not found. Prepare data to create a new one:');
    training_file, testfile, lexicon = prepare_training_data(inp,mode,approach);
    print('Training model');
    model = train_model(training_file);

#If the user has his own testfile, abandon the automatically generated one
if testfile_preset:
    testfile = testfile_preset;

#Go do the prediction in one of the modes, with the model
if mode == 'd':
    demo_mode(model,lexicon,approach,cut_off_lexicon);
elif mode == 's':
    simulation_mode(model,lexicon,testfile,approach,cut_off_lexicon);

#TODO
# ucto inbouwen
# Letter modus perfectioneren
# Server modus
