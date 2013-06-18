import os
import tweetlib

def feed_to_addresseelist(feed):

    try:
        feed = open(feed,'r');
    except IOError:
        return [];

    addressees = [];
    for j in feed:
        try:
            tweet = j.split('||')[2];
        except IndexError:
            print('Skipped one');
            continue;
        addressees += tweetlib.get_addressees(j);

    return addressees;

def find_loose_networks(d):

    networks = [];

    for i in tweeters:
        if i[-1] != '~':

            people_in_network = [i];

            addressees = feed_to_addresseelist(d+'/'+i);
            
            #For each addressee, see if he talks back
            for j in addressees:
                if j not in people_in_network and addressees.count(j) > 2:
                    other_addressees = feed_to_addresseelist(d+'/'+j);
                    if other_addressees.count(i) > 2:
                        print j+' replies to '+i+' '+str(other_addressees.count(i))+' times.';
                        people_in_network.append(j);

            networks.append(people_in_network);

    return networks

def find_close_networks(d):

    #Does not yet do what it is supposed to do

    #files = os.listdir(d);
    networks = [];

    for i in tweeters[:3]:
        print 'Calculating from '+ i;
        if i[-1] != '~':

            people_in_network = set();
            people_in_network.add(i);

            addressees = feed_to_addresseelist(d+'/'+i);
            
            #For each addressee, see if he talks to all others in the network
            for j in addressees:
                other_addressees = feed_to_addresseelist(d+'/'+j);
                
                missed_one = False;
                
                for k in people_in_network:
                    if k not in other_addressees:
                        missed_one = True;
                        break;

                if not missed_one:     
                    people_in_network.add(j);
                    print 'Added '+j+' to '+i;

            #Only add your discovered network when it's uniquef
            if not people_in_network in networks:
                networks.append(people_in_network);

    return networks;

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

networks = find_loose_networks('/scratch/wstoop/tweetdata/feeds');
output = open('communities','w');
        
for i in networks:
    for j in i:
        output.write(j+'\n');

    output.write('\n');

#TODO
# Minimaal zo vaak tegen elkaar gepraat
