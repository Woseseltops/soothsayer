import tweetlib
import sys
import os
import twython

api = twython.Twython();

try:
    tweeters = sys.argv[1];
    feedslib = sys.argv[2];
except:
    tweeterfile_loc = 'C:\\Users\\Stoop\\Desktop\\Scriptie\\tweetdata\\twitteraars.txt';
    feedslib = 'C:\\Users\\Stoop\\Desktop\\Scriptie\\tweetdata\\feeds\\';

#Get all twitter users
tweeterfile = open(tweeterfile_loc,'r');
tweeters = [];

for tweeter in tweeterfile:
    tweeters.append(tweeter[:-1]);

#See if they have tweets we don't have (yet)
for tweeter in tweeters:

    #If we got no data for this user yet, get as much as you can
    if not os.path.isfile(feedslib+tweeter):

        open(feedslib+tweeter,'w');
        feedfile = open(feedslib+tweeter,'a');

        tweets = tweetlib.get_all_tweets(tweeter,api);
        print(len(tweets),tweeter);

        #Process all new tweets
        for tweet in tweets:
            feedfile.write(tweet[0] + '||' + tweet[1]+'\n');

            #If this tweet contains addressees we don't know yet, and the tweet is Dutch,
            #add them to the people we follow
            addressees = tweetlib.get_addressees(tweet[1]);            

            if len(addressees) > 0 and tweetlib.is_dutch(tweet[1]):
                tweeterfile = open(tweeterfile_loc,'a');
                
                for addressee in addressees:                    
                    if addressee not in tweeters:                    
                        tweeterfile.write(addressee+'\n');
                        tweeters.append(addressee);

    #If we do have data, only update        
    else:
        pass;

#TODO
# De twee nieuwe mensen die we volgen zijn de mensen die het meeste worden aangesproken
# door de mensen die we wel volgen
# Update feeds
# Ook tijden opslaan voor tweets
# Is dutch optimizen
