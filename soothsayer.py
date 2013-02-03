import os;
import subprocess;

def command(command,piped = False):

    if piped:
        result = subprocess.Popen(command, shell=True,stdout=subprocess.PIPE).communicate()[0].decode();
    else:
        result = subprocess.Popen(command, shell=True).communicate()[0].decode();

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
    else:
        current_word = words[-1];
        words = words[-4:-1];

    #Make ready for Timbl
    while len(words) < 3:
        words = ['_'] + words;

    lcontext = ' '.join(words) + ' _';
    open('predictions/lcontext','w').write(lcontext);

    #Ask TiMBL for prediction
    command('timbl -t predictions/lcontext -i '+model+' +vdb +D -a1 -G +vcf',True);

    #Turn prediction into list of tuples
    raw_distr = open('predictions/lcontext.IGTree.gr.out','r').read().split('{')[1];
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
    pick = '';
    boundary = len(current_word);

    for i in predictions:
        if i[0][:boundary] == current_word:
            pick = i[0];
            break;
    
    return pick,current_word; 

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
            if prediction != '':
                text_so_far, last_input = add_prediction(text_so_far,prediction);
            else:
                text_so_far += ' ';

        #Reject prediction
        elif char == '\t':
            text_so_far+= ' ';

        #Don't accept prediction
        else:
            text_so_far += char;

        #Predict new word
        prediction,current_word = do_prediction(text_so_far,model);

        #Show the prediction
        clear();
        print(text_so_far+'|'+prediction[len(current_word):]);

        #Check for quit
        if 'quit' in text_so_far.split():
            busy = False;

def prepare_training_data(directory):

    files = os.listdir(directory);
    total_text = '';

    for i in files:
        print(i);
        total_text += ' _ _ _ '+open(directory+i,'r').read();

    ngrams = window_string(total_text.strip())
    training_file_content = '\n'.join(ngrams);
    filename = 'models/'+directory[:-1]+'.training.txt';
    training_file = open(filename,'w');
    training_file.write(training_file_content);
    
    return filename;
    
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

#########

mode = input('Mode (d = demo, s = simulation): ');
inp = input('Input directory (include (back)slash): ');

try:
    open('models/'+inp[:-1]+'.training.txt','r');
    print('Using existing model.');
except:
    f = prepare_training_data(inp);
    train_model(f);
    print('Model not found. Created a new one.');

model = 'models/'+inp[:-1]+'.training.txt.IGTree';

if mode == 'd':
    demo_mode(model);

#Later
# Server modus
# Letter approach
