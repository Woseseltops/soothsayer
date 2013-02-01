import os;

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

def do_prediction(text):

    words = text.split()[-4:-1];

    if 'heet' in words:
        return 'wessel';
    else:
        return('koekjes');

def add_prediction(text,prediction):

    if text[-1] == ' ':
        return text + prediction, ''; #Last input not correct

    else:
        words = text.split();
        last_input = words[-1];
        words = words[:-1];
        words.append(prediction);
        return ' '.join(words) + ' ', last_input;
    
def demo_mode():
    print('Start typing whenever you want');
    
    get_character = get_character_function();

    busy = True;
    text_so_far = '';
    prediction = '';

    while busy:
        char = str(get_character());

        #Accept prediction
        if char == ' ':
            text_so_far, last_input = add_prediction(text_so_far,prediction);

        #Reject prediction
        elif char == '\t':
            text_so_far+= ' ';

        #Don't accept prediction
        else:
            text_so_far += char;

        prediction = do_prediction(text_so_far);

        clear();
        print(text_so_far);
        print();
        print(prediction);

        #Check for quit
        if 'quit' in text_so_far.split():
            busy = False;

def prepare_training_data(directory):

    files = os.listdir(directory);
    total_text = '';

    for i in files:
        total_text += ' _ _ _ '+open(directory+i,'r').read();

    ngrams = window_string(total_text.strip())
    training_file_content = '\n'.join(ngrams);
    training_file = open('training.txt','w');
    training_file.write(training_file_content);
    
    return training_file;
    
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

#########

mode = input('Mode (d = demo, s = simulation): ');
inp = input('Input directory (include (back)slash): ');

f = prepare_training_data(inp);

if mode == 'd':
    demo_mode();

#Later
# Server modus
# Letter approach
