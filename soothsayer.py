import os;
import subprocess;

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

def do_prediction(text,model):
    """Returns a prediction by TiMBL and the word the user is currently typing""";

    #Figure out the left context and the word being worked on
    words = text.split();

    if text == '' or text[-1] == ' ':
        current_word = '';
        words = words[-3:]

        #Make ready for Timbl
        while len(words) < 3:
            words = ['_'] + words;

        lcontext = ' '.join(words) + ' _';
        open('predictions/lcontext','w').write(lcontext);

        #Ask TiMBL for new prediction
        command('timbl -t predictions/lcontext -i '+model+' +vdb +D -a1 -G +vcf');

    else:
        current_word = words[-1];
        words = words[-4:-1];

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

    for i in predictions:
        if i[0][:boundary] == current_word:
            if i[1] > highest_confidence:

                second_pick = pick;
                second_highest_confidence = highest_confidence;
                
                pick = i[0];
                highest_confidence = i[1];
            elif i[1] > second_highest_confidence:
                second_pick = i[0];
                second_highest_confidence = i[1];                
    
    return {'full_word':pick,'word_so_far':current_word,'nr_options':len(predictions),'second_guess':second_pick}; 

def add_prediction(text,prediction):

    if text[-1] == ' ':
        return text + prediction + ' ', '';
    else:
        words = text.split();
        last_input = words[-1];
        words = words[:-1];
        words.append(prediction);
        return ' '.join(words) + ' ', last_input;
    
def demo_mode(model):
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
        prediction = do_prediction(text_so_far,model);

        #Show the prediction
        chars_typed = len(prediction['word_so_far']);
        clear();
        print(text_so_far+'|'+prediction['full_word'][chars_typed:]);
        print();
        print('Or '+prediction['second_guess']+', '+str(prediction['nr_options'])+' options.');

        #Check for quit
        if 'quit' in text_so_far.split():
            busy = False;

def simulation_mode(model,testfile):

    #Prepare vars and output
    teststring = open(testfile,'r').read();
    total_keystrokes_saved = 0;
    total_keystrokes_saved_sk = 0; #Swiftkey measure
    already_predicted = False;
    open('Soothsayer_output','w');
    outputfile = open('Soothsayer_output','a');

    #Go through the testfile letter for letter
    for i in range(len(teststring)):

        if teststring[i] == ' ':
            second_guess_got_it_already = False;

        #If the word was not already predicted, guess (again)
        if not already_predicted:

            #Do prediction and compare with what the user was actually writing
            text_so_far = teststring[:i];
            prediction = do_prediction(text_so_far,model);
            current_word = find_current_word(teststring,i);
            outputfile.write(prediction['word_so_far']+', '+ current_word+', '+prediction['full_word']+'\n');

            #If correct, calculate keystrokes saved and put in output
            if current_word == prediction['full_word']:
                outputfile.write('Correct! Skip to the next word. \n');
                already_predicted = True;

                keystrokes_saved = calculate_keystrokes_saved(prediction['word_so_far'],current_word);
                    
                outputfile.write(str(keystrokes_saved)+' keystrokes saved \n');

                total_keystrokes_saved += keystrokes_saved;
                perc = str(total_keystrokes_saved / len(text_so_far));
                outputfile.write(str(total_keystrokes_saved) + ' of ' + str(len(text_so_far)) + ' keystrokes saved so far, (' +perc+'%) - CKS\n');

                if not second_guess_got_it_already:
                    total_keystrokes_saved_sk += keystrokes_saved;            
                    perc = str(total_keystrokes_saved_sk / len(text_so_far));
                    outputfile.write(str(total_keystrokes_saved_sk) + ' of ' + str(len(text_so_far)) + ' keystrokes saved so far, (' +perc+'%) - SKKS\n');

            elif current_word == prediction['second_guess']:
                outputfile.write('Second guess was correct here. \n');

                keystrokes_saved = calculate_keystrokes_saved(prediction['word_so_far'],prediction['second_guess']);

                total_keystrokes_saved_sk += keystrokes_saved;            

                perc = str(total_keystrokes_saved_sk / len(text_so_far));
                outputfile.write(str(total_keystrokes_saved_sk) + ' of ' + str(len(text_so_far)) + ' keystrokes saved so far, (' +perc+'%) - SKKS\n');

                second_guess_got_it_already = True;
                
        #Skip if the word was already predicted
        else:
            if teststring[i] == ' ':
                already_predicted = False;
                

def find_current_word(string, position):
    """Returns which word the user was typing at this position""";

    word = string[position-1];

    #If starting with a space, give the next word
    while word == ' ':
        position += 1;
        word = string[position-1];

    c = 2;
    while word[0] != ' ':
        word = string[position-c] + word;
        c += 1;

    c = 0;
    while word[-1] != ' ':
        try:
            word +=  string[position+c];
        except IndexError:
            break;
        c += 1;

    return word.strip();

def prepare_training_data(directory,mode):

    #Paste all texts in the directory into one string
    files = os.listdir(directory);
    total_text = '';

    for i in files:
        print(i);
        total_text += ' _ _ _ '+open(directory+i,'r').read();

    #In simulation mode, cut away 10 percent for testing later
    if mode == 's':
        testfilename = 'models/'+directory[:-1]+'.10.test.txt';
        training_filename = 'models/'+directory[:-1]+'.90.training.txt';

        words = total_text.split();
        boundary = round(len(words)*0.9);

        open(testfilename,'w').write(' '.join(words[boundary:]));
        total_text = ' '.join(words[:boundary]);

    #In demo mode, just take all
    else:
        testfilename = '';
        training_filename = 'models/'+directory[:-1]+'.training.txt';

    #Make into ngrams, and save the file
    ngrams = window_string(total_text.strip())
    training_file_content = '\n'.join(ngrams);
    open(training_filename,'w').write(training_file_content);

    #Return the filenames
    return training_filename, testfilename;
    
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

def train_model(filename):
    """Train a model on the basis of these ngrams""";

    command('timbl -f '+filename+' -I '+filename+'.IGTree +D +vdb -a1',True);

    return filename+'.IGTree';

def calculate_keystrokes_saved(word_so_far,prediction):

    keystrokes_saved = len(prediction) - len(word_so_far) - 1;

    if keystrokes_saved < 0:
        keystrokes_saved = 0;
    
    return keystrokes_saved;

######### Script starts here ######################

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
    open('models/'+dir_reference+'.training.txt','r');
    print('Using existing model for '+dir_reference+'.');

    testfile = 'models/'+inp[:-1] + '.10.test.txt';
    model = 'models/'+dir_reference+'.training.txt.IGTree';
except:
    training_file, testfile = prepare_training_data(inp,mode);
    model = train_model(training_file);
    print('Model not found. Created a new one.');

#Go do the prediction in one of the modes, with the model
if mode == 'd':
    demo_mode(model);
elif mode == 's':
    simulation_mode(model,testfile);

#TODO
# Server modus
# Letter approach
