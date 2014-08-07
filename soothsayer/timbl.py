import socket
import time
import soothsayer
import math

try:
    import psutil
except ImportError:
    pass;

class Timbl:
    def __init__(self):
        self.cmdstring = 'timblserver -i %s +vdb +D -a1 -G +vcf -S %d -C 1000'
        self.pid = None
        self.socket = None
        self.neverkillserver = False;

    def start_server(self, igtree, port=None):
        """ Start a new Timbl server"""

        if not port:
            port = self._getnewport()

        r = soothsayer.command(self.cmdstring % (igtree, port));
        return port

    def connect(self, port, host='', retry=20, interval=1):
        """ Connect to a Timbl server"""

        clientsocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        while retry > 0:
            retry -= 1

            try:
                clientsocket.connect((host,int(port)))
                clientsocket.recv(1024) # Ignore welcome messages
                self.socket = clientsocket
                break;
            except socket.error:
                time.sleep(interval)
                continue

        #Get PID
        pidlist = psutil.get_pid_list();
        for i in reversed(pidlist):
            try:
                p = psutil.Process(i);
            except psutil._error.NoSuchProcess:
                continue;

            if len(p.cmdline) > 9 and p.cmdline[9] == str(port):
                self.pid = i;
                break;

        print(self.socket);

        return True
    
    def findport(self, modelname):
        """ Find an existing Timbl server by model name"""
        pidlist = psutil.get_pid_list();

        for i in reversed(pidlist):

            try:
                p = psutil.Process(i);
            except psutil.NoSuchProcess:
                #Sometimes it turns out the process does not really exist
                continue;

            if len(p.cmdline) > 9 and p.cmdline[2] == modelname:
                port = int(p.cmdline[9]);
                return port

    def _getnewport(self):
        """ Get a free port """
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.bind(('',0))
        port = s.getsockname()[1]
        s.close()

        return int(port)

    def send(self,message):

        self.socket.sendall(message)

    def receive(self):

        return self.socket.recv(1024).decode()

    def __del__(self):
        """Remove the corresponding Timblserver, if there is one""";
        
        if not self.neverkillserver:
            print('Killing process '+str(self.pid));
            soothsayer.command('kill '+str(self.pid));

def divide_iterable(it,n,overlap=None):
    """Returns any iterable into n pieces"""

    save_it = it
    piece_size = math.ceil(len(it) / n)
    result = []
    while len(it) > 0:
        result.append(it[:piece_size])
        it = it[piece_size:]

    #If not enough pieces, divide the last piece
    if len(result) != n:
        last_piece = result[-1]
        boundary = round(len(last_piece)/2)
        result.append(last_piece[boundary:])
        result[-2] = last_piece[:boundary]

    #Add overlap if needed
    if overlap:
        for n,i in enumerate(result):

            #Add left overlap
            pos = piece_size * n
            result[n] = save_it[pos-overlap:pos] + result[n]

    return result

def window_string_letters(string,verbose = False):
    """Return the string as a list of letter 15-grams"""

    words = string.split()
    newstring = string.replace(' ','_').replace('\n','')
    ngrams = []
    
    for i in range(0,len(string)+1):

        current_word = find_current_word(newstring, i).replace('_','')
        letters_before = ' '.join(newstring[i-15:i])
        if len(letters_before) > 1:
            if len(current_word) > 1 and letters_before[-1] != '_':
                letters_before = current_word[0] + letters_before[1:]
            else:
                letters_before = '_' + letters_before[1:]

            ngrams.append(letters_before + ' ' +current_word)

    #Remove useless ones
    ngrams_to_remove = []
    for n,i in enumerate(ngrams):
        words = i.split()
        if i[-1] == '_' or len(words) != 16 or i == ngrams[-1]:
            ngrams_to_remove.append(i)

#    for i in ngrams_to_remove:
#        ngrams.remove(i)

    return ngrams[1:-1]

def window_string(string,verbose = False):
    """Return the string as a list of 4-grams"""

    if not isinstance(string,list):
        words = string.split()
    else:
        words = string

    word_nr = len(words)
    ngrams = []
    
    for n,i in enumerate(range(0,len(words)-3)):
        ngrams.append(' '.join(words[i:i+4]))

    #Remove useless ones
    ngrams_to_remove = []
    for n,i in enumerate(ngrams):
        if i[-1] == '_':
            ngrams_to_remove.append(i)

#    for i in ngrams_to_remove:
#        ngrams.remove(i)

    return ngrams

