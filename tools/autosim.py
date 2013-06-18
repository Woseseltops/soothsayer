import os
import subprocess

def already_done():
    files = os.listdir('/vol/bigdata/users/wstoop/soothsayer/output');
    done = [];
    
    for i in files:
        if 'Soothsayer_output' in i:
            done.append(i.split('.')[-1]);

    return done;               

def command(command,piped = False):

    if piped:
        result = subprocess.Popen(command, shell=True,stdout=subprocess.PIPE).communicate()[0].decode();
    else:
        f = open('output_mass_sim','w');
        result = subprocess.Popen(command, shell=True);
        result.wait();

    return(result);

tweeters = ['4rch1t3ct', 'corriebult', 'jboekelman', 'megasupernieuws', 'sredlums',
            'aafkebrons', 'deesje34', 'jdpoohbear', 'micheldebruijn', 'steephsel',
            'aardengelpiet', 'deheldin', 'jennekepenneke', 'miekeinc', 'tasvolverhalen',
            'agatha_make_up', 'dennismons', 'jessiesissammy', 'mitzyoss', 
            'aldith_hunkar', 'devrouwthuis', 'jettyvanrooy', '_mrs', 'texas12345',
            'eetschrijver', 'jndkgrf', 'mrsmartine', 'the_ed', 'amadeusivan', 'elmavonk',
            'johnschop', 'musjes', 'tibetanpaddy', 'a_mieke', 'erwblo', 'josvrbk',
            'nabilfeki', 'tien020', 'analons', 'esther_305', 'karinwinters',
            'titchener', 'ewdevlieger', 'klapster', 'tourdejose',
            'anniebbarks', 'fluist3r', 'knotsbots', 'tponl', 'archatoz', 'fred3012',
            'kos_', 'ongerijmd', 'tvgeneuzel', 'artbysophia', 'godpipo', 'k_ruiter',
            'paulzornig', 'umarebru', 'baspaternotte', 'goedemorgenman', 'leolewin',
            'peterstafleu', 'vic23', 'bas_taart', 'gradjuh', 'lexcje', 'pienbetuwe',
            'victorward', 'beanobrien13', 'harveycusick', 'liekelamb', 'pinaatje',
            'walterhoekstra', 'henkkanning', 'lobdozer', 'politicus1',
            'whippetpickle', 'boswachterfrans', 'hetspijtme', 'puberdochters', 'wup5',
            'brechtjedeleij', 'house_fd', 'mariannecramer', 'rebelsnotes', 'w_veldhorst',
            'casvries', 'humfthecocker', 'marjasandersnl', 'rider_ot_storm',
            'zijhiernaast', 'chrisklomp', 'ikke_mij_deze', 'marktwain2', 'rjvanhouten',
            'contentgirl', 'jasmijn02', 'maupienco', 'roosvanvugt'];

excep = [];

for i in tweeters:
    if i not in already_done() and i not in excep:
        print('Started with '+str(i));
#        command('python3 ss_standalone.py -w -s -id '+i,False);
        command('python3 ss_standalone.py -w -s -id fakecomm_'+i+' -tf wordmodels/'+i+'.10.test.txt -cf '+i,False);
        command('mv output/Soothsayer_output output/Soothsayer_output.'+str(i),True);
        print('Completed '+ str(i));

print('Done with everything');        
