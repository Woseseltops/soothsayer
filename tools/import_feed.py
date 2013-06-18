import sys
import os

for i in sys.argv[1:]:
    print('%',i);
    f = open('/scratch/wstoop/tweetdata/feeds/'+i);
    tweets = [];
    for j in f:
        try:
            tweets.append(j.split('||')[2]);
        except IndexError:
            print('Skipped one');
    
    try:
        os.mkdir(i);
    except OSError:
        pass;

    open(i+'/'+i,'w').write(''.join(tweets));
