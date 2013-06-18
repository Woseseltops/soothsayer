import sys
import os
import operator

loc = '/scratch/wstoop/tweetdata/feeds/';
goal = '/vol/bigdata/users/wstoop/soothsayer/input/';

#Get the 100 largest files
getall = [ [f, os.path.getsize(loc+f)] for f in os.listdir(loc) ]
files = sorted(getall, key=operator.itemgetter(1),reverse=True)
largest_feeds = [];

for f in files:
    name = f[0];
    if name not in ['klm','ns_online','nos','kpnwebcare','tmobile_webcare',
                    'vodafonenl','upc','albertheijn','telegraaf','anwb_verkeer',
                    'ingnl_webcare','anwbverkeer']:
        largest_feeds.append(name);

    if len(largest_feeds) > 99:
        break;

for i in largest_feeds:
    print('%',i);
    f = open(loc+i);
    tweets = [];
    for j in f:
        try:
            tweets.append(j.split('||')[2]);
        except IndexError:
            print('Skipped one');
    
    try:
        os.mkdir(goal+i);
    except OSError:
        pass;

    open(goal+i+'/'+i,'w').write(''.join(tweets));
