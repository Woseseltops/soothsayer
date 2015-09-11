import tweetlib
import sys
import os

#Folders and files needed
inputfolder = '/scratch2/www/soothsayer/repo/soothsayer/input/';

#Import tweets for user
twitter_user = sys.argv[1];
tweets = tweetlib.get_all_tweets(twitter_user,passwords='/scratch2/www/soothsayer/webdemo/passwords.txt');

#Make directory and file
os.makedirs(inputfolder+twitter_user);
filename = inputfolder+twitter_user+'/'+twitter_user;

open(filename,'w'); 
f = open(filename,'a');

#Fill with the tweets
for i in tweets:
    f.write(i[2]);

#TODO
# Wat als de gebruikers een niet-bestaande naam intikt?
