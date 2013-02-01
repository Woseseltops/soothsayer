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

def demo_mode():
    print('Start typing whenever you want');
    
    get_character = get_character_function();

    busy = True;
    text_so_far = '';

    while busy:
        char = str(get_character());
        text_so_far += char;

        clear();
        print(text_so_far);
        print();
        print(do_prediction(text_so_far));

        if 'quit' in text_so_far.split():
            busy = False;

#########

mode = input('Mode (d = demo, s = simulation): ');

if mode == 'd':
    demo_mode();
