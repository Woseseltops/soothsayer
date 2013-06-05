import copy
import random

f = open('tweeters','r');
tweeters = [i.strip() for i in f];

folder_from = copy.copy(tweeters);

for i in tweeters:
    c = random.choice(folder_from);
    folder_from.remove(c);
    print i, c;
