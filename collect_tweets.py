import tweetlib
import sys
import os
import twython
import random
import sys

api = twython.Twython();

try:
    tweeterfile_loc = sys.argv[1];
    feedslib = sys.argv[2];
except:
    tweeterfile_loc = 'C:\\Users\\Stoop\\Desktop\\Scriptie\\tweetdata\\twitteraars.txt';
    feedslib = 'C:\\Users\\Stoop\\Desktop\\Scriptie\\tweetdata\\feeds\\';

#Get all tweeters, and shuffle them (so we don't always start with the same)
tweeterfile = open(tweeterfile_loc,'r');
tweeters = [];

for tweeter in tweeterfile:
    tweeters.append(tweeter[:-1]);

random.shuffle(tweeters);

#See if they have tweets we don't have (yet)
for tweeter in tweeters[:25]:

    if tweeter == '':
        continue;

    #If we got no data for this user yet, get as much as you can
    if not os.path.isfile(feedslib+tweeter):

        tweets = tweetlib.get_all_tweets(tweeter,api);
        tweets.reverse();
        print('Added',len(tweets),'tweets for',tweeter);

        if len(tweets) > 0:
            open(feedslib+tweeter,'w');
            feedfile = open(feedslib+tweeter,'a');

            for tweet in tweets:
                feedfile.write(tweet[0] + '||' + tweet[1] + '||' + tweet[2]+'\n');

    #If we do have data, only update        
    else:
        
        #Get all id you already know
        feedfile = open(feedslib+tweeter,'r').readlines();        
        ids_collected = [];

        for line in feedfile:
            ids_collected.append(line.split('||')[0]);

        #Reverse the list, so the new ones are the ones seen first
        ids_collected.reverse();

        #Get new tweets, and compare their ids to the ones you already have
        found_match = False;
        number = 20;
        tries = 0;

        while not found_match and tries < 4:
            tweets = tweetlib.get_recent_tweets(tweeter,number,api);    
            tweets.reverse();

            if len(tweets) == 0:
                break;

            for tweet in tweets:
                if tweet[0] in ids_collected:
                    found_match = True;
                    break;

            if not found_match:
                print('No match found, asking for more data!');
                number *= 4;

            tries += 1;

        feedfile = open(feedslib+tweeter,'a');

        for tweet in tweets:
            if tweet[0] not in ids_collected:
                print('New tweet found:',tweet[2]);
                feedfile.write(tweet[0] + '||' + tweet[1] + '||' + tweet[2]+'\n');

#Add new tweeters to the list
tweeter1, tweeter2 = tweetlib.get_new_tweeters(feedslib,tweeters[:35]);
open(tweeterfile_loc,'a').write(tweeter1+'\n'+tweeter2+'\n');
print('Added',tweeter1,tweeter2);

#TODO
# Remove tweeters with closed profiles
