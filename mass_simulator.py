import subprocess

#This scripts let you run a program multiple times with various configurations, and
# renames the output after the particular configuration you were using

def command(command,piped = False):

    if piped:
        result = subprocess.Popen(command, shell=True,stdout=subprocess.PIPE).communicate()[0].decode();
    else:
        f = open('output','w');
        result = subprocess.Popen(command, shell=True,stdout=f,stderr=f);
        result.wait();

    return(result);

configs = [1,2,3];

for i in configs:
    command('python hundred.py',True);
    command('mv outputje outputje.'+str(i),True);
    print('Completed '+ str(i));
