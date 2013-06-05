import sys
import os

if sys.argv[1] == '-R':
    files = os.listdir(sys.argv[2]);
    for i in files:
        words = open(sys.argv[2]+'/'+i,'r').read().replace('\n',' ').split();
#        print(i,len(words));        
#        print(len(words));
        print(len(open(sys.argv[2]+'/'+i,'r').readlines()));
else:
    words = open(sys.argv[1],'r').read().replace('\n',' ').split();
    print(len(words));
