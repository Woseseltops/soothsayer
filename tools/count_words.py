import sys
import os

if sys.argv[1] == '-R':
    direc = sys.argv[2];
    files = os.listdir(direc);
    for i in files:        
        if os.path.isfile(direc+'/'+i):
            words = open(direc+'/'+i,'r').read().replace('\n',' ').split();
    #        print(i,len(words));        
    #        print(len(words));
            print(i,len(open(direc+'/'+i,'r').readlines()));
        else:            
            subfiles = os.listdir(direc+'/'+i);
        
            for j in subfiles:
                if 'community' not in i and 'nl' not in i and 'allmail' not in i and 'andrekuipers' not in i:    
                    try:
                        words = open(direc+'/'+i+'/'+j,'r').read().replace('\n',' ').split();
                        print(j,len(words));
    #                    print(j,len(open(direc+'/'+i+'/'+j,'r').readlines()));                
                    except UnicodeDecodeError:
                        pass;
else:
    words = open(sys.argv[1],'r').read().replace('\n',' ').split();
    print(len(words));
