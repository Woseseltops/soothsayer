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

tweeters = ['artbysophia','baspaternotte','marktwain2','pinaatje','pienbetuwe',
            'rider_ot_storm','mrsmartine','chrisklomp','leolewin','contentgirl',
            'amadeusivan','ongerijmd','umarebru','a_mieke','steephsel','brechtjedeleij',
            'eetschrijver','esther_305','klapster','goedemorgenman','walterhoekstra',
            'jasmijn02','miekeinc','sredlums','aldith_hunkar','tien020','karinwinters',
            'johnschop','lobdozer','theollieworks','wup5','jennekepenneke','rebelsnotes',
            'puberdochters','knotsbots','dennismons','fluist3r','mariannecramer',
            'rjvanhouten','superjan','titchener','anniebbarks','fred3012','politicus1',
            'peterstafleu','jettyvanrooy','mariannezw','jochemgeerdink','nabilfeki',
            'kos_'];

networks = find_loose_networks('/scratch/wstoop/tweetdata/feeds');
output = open('communities','w');
        
for i in networks:
    for j in i:
        output.write(j+'\n');

    output.write('\n');

#TODO
# Minimaal zo vaak tegen elkaar gepraat
