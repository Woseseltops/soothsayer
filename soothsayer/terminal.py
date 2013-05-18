import os

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

    return function        

def clear():
    """Clears the screen"""

    os.system(['clear','cls'][os.name == 'nt'])

colors = {'PERS. MODEL/IGTREE': '\033[0;35m', 'PERS. MODEL/LEXICON': '\033[1;34m',
          'GEN. MODEL/IGTREE': '\033[0;32m', 'GEN. MODEL/LEXICON': '\033[1;31m',
          'RECENCY BUFFER': '\033[1;31m', 'white': '\033[0m', 'I GIVE UP': '\033[0m',
          'USER': '\033[0m', 'PERS. MODEL/IGTREE +RB': '\033[1;31m',
          'GEN. MODEL/IGTREE +RB': '\033[1;31m'};
