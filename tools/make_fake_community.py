import shutil
import os
import random

#Pick a random dir
def random_feed(all_files):
    r_dirname = random.choice(list(all_files.keys()));
    r_dir = all_files[r_dirname];
    r_file = random.choice(r_dir);

    return r_file, 'input/'+r_dirname+'/'+r_file;

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

#Get dict with all files
all_files = {}
f = os.listdir('input');

for i in f:
    if 'community' in i:
        all_files[i] = os.listdir('input/'+i);

#Create the fake community
for i in tweeters:

    #Create dir
    community = 'input/fakecomm_'+i;
    os.mkdir(community);
    files_in_fake = [];
    files_in_original = os.listdir('input/community_'+i);
    
    #Add idiolect
    shutil.copyfile('input/'+i+'/'+i,'input/fakecomm_'+i+'/'+i);

    #Replace all in original with new one
    for j in files_in_original[:-1]:

        while True:
            name,loc = random_feed(all_files);

            if name not in files_in_original+files_in_fake:
                shutil.copyfile(loc,'input/fakecomm_'+i+'/'+name);
                files_in_fake.append(name);
                break;
            

##f = open('fakecom_couples','r');
##
##for i in f:
##
##    name,source = i.split();
##
##    print('Creates fake community for',name);
##    shutil.copytree('community_'+source,'fakecomm_'+name);
##    
##    print('Removes file',source);
##    os.remove('fakecomm_'+name+'/'+source);
##
##    print('Add file',name);
##    shutil.copyfile(name+'/'+name,'fakecomm_'+name+'/'+name);
