import socket
import terminal
import gettimbleserverport
import time
import psutil

class Timbl:
    def __init__(self):
        self.cmdstring = 'timblserver -i %s.training.txt.IGTree +vdb +D -a1 -G +vcf -S %d -C 1000'

        self.socket = None


    def startserver(self, model, port=None):
        """ Start a new Timbl server"""
        if not port:
            port = self._getnewport()
        
        terminal.command(self.cmdstring % (model, port))

    def connect(self, host=None, port, retry=10, interval=1):
        """ Connect to a Timbl server"""

        clientsocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        
        if not host:
            host = ''

        while retry > 0:
            retry -= 1

            try:
                clientsocket.connect((host,port))
                clientsocket.recv(1024) # Ignore welcome messages
                self.socket = clientsocket
                return True
            except socket.error:
                time.sleep(interval)
                continue

    def findport(self, model):
        """ Find an existing Timbl server by model name"""
        pidlist = psutil.get_pid_list();
        
        for i in reversed(pidlist):
            p = psutil.Process(i);
            if len(p.cmdline) > 9 and p.cmdline[2] == model:
                port = int(p.cmdline[9]);
                return port

    def _getnewport(self):
        """ Get a free port """
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.bind(('',0))
        port = s.getsockname()[1]
        s.close()

        return int(port)

if __name__ == "__main__":
    timbl = Timbl()

    
