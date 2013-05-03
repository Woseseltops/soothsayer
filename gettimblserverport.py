import psutil
import sys

"""Find a specific Timbl-process and return its listening port"""
def getport(modelfile):
    pidlist = psutil.get_pid_list();
    port = 0
    
    for i in reversed(pidlist):
        p = psutil.Process(i);
        if len(p.cmdline) > 9 and p.cmdline[2] == modelfile:
            port = int(p.cmdline[9]);
            break

    return port;
    
if __name__ == "__main__":
    modelfile = sys.argv[1]
    print getport(modelfile)
