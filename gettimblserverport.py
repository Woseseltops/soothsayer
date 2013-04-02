import psutil
import sys

pidlist = psutil.get_pid_list();

foundit = False;

for i in pidlist[::-1]:
    p = psutil.Process(i);
    if len(p.cmdline) > 9 and p.cmdline[2] == sys.argv[1]:
        print int(p.cmdline[9]);
        foundit = True;
        break;

if not foundit:
    print 0;
