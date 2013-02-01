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

    words = text.split();

    if 'heet' in words:
        return 'wessel';
    else:
        return('koekjes');

def add_prediction(text,prediction):

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

#########

mode = input('Mode (d = demo, s = simulation): ');

if mode == 'd':
    demo_mode();
