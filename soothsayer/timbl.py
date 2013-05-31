import socket
import time
import psutil
import soothsayer

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
        
        soothsayer.command(self.cmdstring % (igtree, port))

        return port

    def connect(self, port, host='', retry=10, interval=1):
        """ Connect to a Timbl server"""

        clientsocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        while retry > 0:
            retry -= 1

            try:
                clientsocket.connect((host,int(port)))
                clientsocket.recv(1024) # Ignore welcome messages
                self.socket = clientsocket
            except socket.error:
                time.sleep(interval)
                continue

        #Get PID
        pidlist = psutil.get_pid_list();
        for i in reversed(pidlist):
            p = psutil.Process(i);
            if len(p.cmdline) > 9 and p.cmdline[9] == str(port):
                self.pid = i;
                break;

        return True
    
    def findport(self, modelname):
        """ Find an existing Timbl server by model name"""
        pidlist = psutil.get_pid_list();
        
        for i in reversed(pidlist):
            p = psutil.Process(i);
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
