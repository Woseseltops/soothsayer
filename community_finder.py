import os
import tweetlib

files = os.listdir('testfeeds');

def feed_to_addresseelist(feed):

    feed = open(feed);

    addressees = [];
    for j in feed:
        addressees += tweetlib.get_addressees(j);

    return addressees;

def find_loose_networks():

    networks = [];

    for i in files:
        if i[-1] != '~':

            name = i[:-4];
            people_in_network = [name];

            addressees = feed_to_addresseelist('testfeeds/'+i);
            
            #For each addressee, see if he talks back
            for j in addressees:
                other_addressees = feed_to_addresseelist('testfeeds/'+j+'.txt');
                if name in other_addressees:
                    people_in_network.append(j);

            networks.append(people_in_network);

    return networks

def find_close_networks():

    networks = [];

    for i in files:
        if i[-1] != '~':

            name = i[:-4];
            people_in_network = set();
            people_in_network.add(name);

            addressees = feed_to_addresseelist('testfeeds/'+i);
            
            #For each addressee, see if he talks to all others in the network
            for j in addressees:
                other_addressees = feed_to_addresseelist('testfeeds/'+j+'.txt');
                
                missed_one = False;
                
                for k in people_in_network:
                    if k not in other_addressees:
                        missed_one = True;
                        break;

                if not missed_one:     
                    people_in_network.add(j);

            #Only add your discovered network when it's uniquef
            if not people_in_network in networks:
                networks.append(people_in_network);

    return networks

print(find_close_networks());
        
#TODO
# Minimaal zo vaak tegen elkaar gepraat
