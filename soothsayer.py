import os;
import subprocess;
import sys;
import time;

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

def do_prediction(text,model,lexicon,approach):
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

            lcontext = attenuate_string(' '.join(words) + ' _',lexicon);
            open('predictions/lcontext','w').write(lcontext);

            #Ask TiMBL for new prediction
            command('timbl -t predictions/lcontext -i '+model+' +vdb +D -a1 -G +vcf');

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
    raw_distr = open('predictions/lcontext.IGTree.gr.out','r').read().split('{');
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
    
    return {'full_word':pick,'word_so_far':current_word,'nr_options':len(predictions),
            'second_guess':second_pick,'third_guess':third_pick}; 

def add_prediction(text,prediction):

    if text[-1] == ' ':
        return text + prediction + ' ', '';
    else:
        words = text.split();
        last_input = words[-1];
        words = words[:-1];
        words.append(prediction);
        return ' '.join(words) + ' ', last_input;
    
def demo_mode(model,lexicon,approach):
    print('Start typing whenever you want');
    
    get_character = get_character_function();

    busy = True;
    text_so_far = '';
    prediction = '';

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
        prediction = do_prediction(text_so_far,model,lexicon,approach);

        #Show the prediction
        chars_typed = len(prediction['word_so_far']);
        clear();
        print(text_so_far+'|'+prediction['full_word'][chars_typed:]);
        print();
        print(prediction['second_guess']+', '+prediction['third_guess']+', '+str(prediction['nr_options'])+' options.');

        #Check for quit
        if 'quit' in text_so_far.split():
            busy = False;

def simulation_mode(model,lexicon,testfile,approach):

    #Prepare vars and output
    starttime = time.time();
    teststring = open(testfile,'r').read();
    total_keystrokes_saved = 0;
    total_keystrokes_saved_sk = 0; #Swiftkey measure
    already_predicted = False;
    open('Soothsayer_output','w');
    outputfile = open('Soothsayer_output','a');

    #Go through the testfile letter for letter
    for i in range(len(teststring)):

        if teststring[i] == ' ':
            skks_got_it_already = False;

        #If the word was not already predicted, guess (again)
        if not already_predicted:

            #Do prediction and compare with what the user was actually writing
            text_so_far = teststring[:i];
            prediction = do_prediction(text_so_far,model,lexicon,approach);
            current_word = find_current_word(teststring,i);
            outputfile.write(prediction['word_so_far']+', '+ current_word+', '+prediction['full_word']+'\n');

            #If correct, calculate keystrokes saved and put in output
            if current_word == prediction['full_word']:
                outputfile.write('## Correct! Skip to the next word. \n');
                already_predicted = True;

                keystrokes_saved = calculate_keystrokes_saved(prediction['word_so_far'],current_word);
                    
                outputfile.write('## ' + str(keystrokes_saved)+' keystrokes saved \n');

                total_keystrokes_saved += keystrokes_saved;
                perc = str(total_keystrokes_saved / len(text_so_far));
                outputfile.write('## ' + str(total_keystrokes_saved) + ' of ' + str(len(text_so_far)) + ' keystrokes saved so far, (' +perc+'%) - CKS\n');

                if not skks_got_it_already:
                    total_keystrokes_saved_sk += keystrokes_saved;            
                    perc = str(total_keystrokes_saved_sk / len(text_so_far));
                    outputfile.write('## ' + str(total_keystrokes_saved_sk) + ' of ' + str(len(text_so_far)) + ' keystrokes saved so far, (' +perc+'%) - SKKS\n');

                outputfile.write('%% Duration so far: '+str(time.time() - starttime)+' seconds \n');

            elif current_word == prediction['second_guess']:
                outputfile.write('## Second guess was correct here. \n');

                keystrokes_saved = calculate_keystrokes_saved(prediction['word_so_far'],prediction['second_guess']);

                total_keystrokes_saved_sk += keystrokes_saved;            

                perc = str(total_keystrokes_saved_sk / len(text_so_far));
                outputfile.write('## ' + str(total_keystrokes_saved_sk) + ' of ' + str(len(text_so_far)) + ' keystrokes saved so far, (' +perc+'%) - SKKS\n');

                skks_got_it_already = True;

            elif teststring[i-1] == ' ' and current_word == prediction['third_guess']:
                outputfile.write('## Third guess was correct here. \n');

                keystrokes_saved = calculate_keystrokes_saved(prediction['word_so_far'],prediction['third_guess']);

                total_keystrokes_saved_sk += keystrokes_saved;            

                perc = str(total_keystrokes_saved_sk / len(text_so_far));
                outputfile.write('## ' + str(total_keystrokes_saved_sk) + ' of ' + str(len(text_so_far)) + ' keystrokes saved so far, (' +perc+'%) - SKKS\n');

                skks_got_it_already = True;
                
        #Skip if the word was already predicted
        else:
            if teststring[i] == ' ':
                already_predicted = False;
                

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
    files = os.listdir(directory);
    total_text = '';

    for i in files:
        print(i);

        if approach == 'w':
            total_text += ' _ _ _ '+open(directory+i,'r').read();
        elif approach == 'l':
            total_text += ' ________________ '+open(directory+i,'r').read();

    #Create and load lexicon
    lexicon_filename = foldername+'/'+directory[:-1]+'.lex.txt'; 
    string_to_lexicon(total_text,lexicon_filename);
    lexicon = load_lexicon(lexicon_filename,20);

    #In simulation mode, cut away 10 percent for testing later
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
    total_text = attenuate_string(total_text,lexicon);

    #Make into ngrams, and save the file
    if approach == 'w':
        ngrams = window_string(total_text.strip());
    elif approach == 'l':
        ngrams = window_string_letters(total_text.strip());

    training_file_content = '\n'.join(ngrams);
    open(training_filename,'w').write(training_file_content);

##    #Attenuate the training file
##    attenuate_training_file(training_filename,lexicon);    

    #Return the filenames
    return training_filename, testfilename, lexicon;
    
def window_string(string):
    """Return the string as a list of 4-grams""";

    words = string.split();
    ngrams = [];
    
    for i in range(0,len(words)-3):
        ngrams.append(' '.join(words[i:i+4]));

    #Remove useless ones
    ngrams_to_remove = [];
    for i in ngrams:
        if i[-1] == '_':
            ngrams_to_remove.append(i);

    for i in ngrams_to_remove:
        ngrams.remove(i);

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

    command('timbl -f '+filename+' -I '+filename+'.IGTree +D +vdb -a1',True);

    return filename+'.IGTree';

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
    frequent_words = [];

    for i in lexicon:
        word,frequency = i.split();
        frequency = int(frequency);

        if frequency > threshold:
            frequent_words.append(word);

    print(len(frequent_words));

    return frequent_words;

def attenuate_string(string,lexicon):
    """Replaces infrequent words in string with #DUMMY""";

    words = string.split();

    result = '';
    for i in words:
        if i not in lexicon and i not in ['_']:
            result += ' #DUMMY';
        else:
            result += ' '+i;

    return result.strip();

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

######### Script starts here ######################

#Try to find arguments
try:
    if sys.argv[1] == '-l':
        approach = 'l';
        modelfolder = 'lettermodels';
        print('Using the letter approach instead of the word approach.');
except IndexError:
    approach = 'w';    
    modelfolder = 'wordmodels';

#Ask for mode and input directory
mode = input('Mode (d = demo, s = simulation): ');
inp = input('Input directory (include (back)slash): ');

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
    model = modelfolder+'/'+dir_reference+'.training.txt.IGTree';
    lexicon = load_lexicon(modelfolder+'/'+dir_reference+'.lex.txt',20);
except:
    training_file, testfile, lexicon = prepare_training_data(inp,mode,approach);
    model = train_model(training_file);
    print('Model not found. Created a new one.');

#Go do the prediction in one of the modes, with the model
if mode == 'd':
    demo_mode(model,lexicon,approach);
elif mode == 's':
    simulation_mode(model,lexicon,testfile,approach);

#TODO
# Alles via argumenten mogelijk maken
# Letter modus perfectioneren
# Attenuation perfectioneren
# Alle metingen heel nauwkeurig doen
# Server modus
