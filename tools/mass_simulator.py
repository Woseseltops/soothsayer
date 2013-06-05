import subprocess
import sys

#This scripts let you run a program multiple times with various configurations, and
# renames the output after the particular configuration you were using

def command(command,piped = False):

    if piped:
        result = subprocess.Popen(command, shell=True,stdout=subprocess.PIPE).communicate()[0].decode();
    else:
        f = open('output_mass_sim','w');
        result = subprocess.Popen(command, shell=True);
        result.wait();

    return(result);

configs = sys.argv[1:];

for i in configs:
    print('Started with '+str(i));
    command('python3 soothsayer.py -w -s -id '+i,False);
    command('mv output/Soothsayer_output output/Soothsayer_output.'+str(i),True);
    print('Completed '+ str(i));
