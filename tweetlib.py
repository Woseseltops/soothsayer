import twython as t
import operator
import os

def get_all_tweets(user,api=None):
    """Returns as much tweets as possible for this twitter user""";

    if api==None:
        api = t.Twython();

    no_tweets = False;
    tweets_total = [];
    c = 1;

    while not no_tweets:
        try:
            tweets = api.getUserTimeline(screen_name=user,count=200,page=c);
        except t.TwythonError:
            tweets = [];
            print('Twython is sad :(');

        if len(tweets) < 1:
            no_tweets = True;
        else:
            for tweet in tweets:
                tweets_total.append((str(tweet['id']),str(tweet['created_at']),clean_tweet(tweet['text'].encode('utf8'),0)));

        c+= 1;

    return tweets_total;

def get_recent_tweets(user,number,api=None):
    """Returns number recent tweets for this twitter user""";

    if api==None:
        api = t.Twython();

    tweets_total = [];

    try:
        tweets = api.getUserTimeline(screen_name=user,count=number);
    except t.TwythonError:
        tweets = [];
        print('Twython is sad :(');

    for tweet in tweets:
        tweets_total.append((str(tweet['id']),str(tweet['created_at']),
                             clean_tweet(tweet['text'].encode('utf8'),0)));

    return tweets_total;

def clean_tweet(tweet,severity=2):
    """Removes links, hastags, smilies, addressees""";

    result = tweet.replace('\n','');

    if severity > 1:
        triggers = ['@','#','http',':',';'];

        words = result.split();
        clean_words = [];

        for i in words:
            found_trigger = False;
            
            for j in triggers:
                if j in i:
                    found_trigger = True;
                    break;

            if found_trigger:
                continue;

            clean_words.append(i);

            result = ' '.join(clean_words)

    return result;

def get_addressees(tweet):
    """Returns all people this tweet was addressed to""";
    
    words = tweet.split(' ');
    addressees = [];
    for i in words:
        if len(i) > 0 and i[0] == '@':
            addressees.append(i.replace('@','').replace(':','').replace(',','').replace('.',''));

    return addressees;

def is_dutch(tweet,word_list = None):
    """Returns whether a tweet is Dutch or not""";

    words = clean_tweet(tweet).split();

    #Half of the words should be in the list
    amount_dutch_threshold = round(len(words) / 2);

    #Import the list
    if word_list == None:
        word_list = get_dutch_wordlist();

    #See how much words are in the list
    found_in_list = 0;

    for i in word_list:
        if i in words:
            found_in_list += 1;

            #Enough words Dutch? Return true
            if found_in_list >= amount_dutch_threshold:
                return True;
                break;

    return False;

def get_dutch_wordlist():
    """Returns a list of the most frequent Dutch words""";

    lines = open(os.getcwd+'nl.txt','r').readlines();
    words = [];

    for i in lines:
        word,frequency = i.split(' ');
        word = word.strip();
        frequency = int(frequency);

        if frequency > 200:
            words.append(word);
    
    return(words);

def get_new_tweeters(feeddir,tweeters):
    """Returns the addressee most mentioned and the addressee most people tweet to""";

    #Get all addressees
    total_addressees = [];
    files = os.listdir(feeddir);

    for f in files:
        print('Getting addressees from',f);
        total_addressees.append(get_all_addressees_from(feeddir+f));

    #Figure out which are most mentioned
    most_mentioned_addressees = most_frequent_first(sum_dicts(total_addressees));
    addressees_most_people_refer_to = most_frequent_first(most_used_keys(total_addressees));

    #Get the two most frequent
    most_mentioned_addressee = '';
    addressee_most_people_refer_to = '';

    print(most_mentioned_addressees[:20]);

    for i in most_mentioned_addressees:
        if i[0].lower() not in tweeters:
            most_mentioned_addressee = i[0].lower();
            break;

    print(addressees_most_people_refer_to[:20]);

    for i in addressees_most_people_refer_to:
        if i[0].lower() not in tweeters and i[0] != most_mentioned_addressee:
            addressee_most_people_refer_to = i[0].lower();
            break;

    return most_mentioned_addressee,addressee_most_people_refer_to;

def get_all_addressees_from(fileloc):
    """Return all addressees mentioned in this file as a dictionary with frequencies""";

    wordlist = get_dutch_wordlist();
    addressees_total = {};
    f = open(fileloc,'r');
    for line in f:
        tweet = line.split('||')[2];
        addressees = get_addressees(tweet);
        if len(addressees) > 0 and is_dutch(tweet,wordlist):
            for addressee in addressees:
                try:
                    addressees_total[addressee] += 1;
                except KeyError:
                    addressees_total[addressee] = 1;

    return addressees_total;

def sum_dicts(dicts):
    """Ads up similar elements in multiple dicts""";

    dict1 = {};

    for d in dicts:
        dict2 = d;
        for k,v in dict2.items():
            try:
                dict1[k] += v;
            except KeyError:
                dict1[k] = v;

    return dict1;

def most_used_keys(dicts):
    """Returns the keys most used in a series of keys""";

    score = {};

    for d in dicts:
        for k in d.keys():
            try:
                score[k] += 1;
            except KeyError:
                score[k] = 1;

    return score;    

def most_frequent_first(d):
    """Changes a dict into a sorted list of key-value tuples, highest value first""";

    d = sorted(d.iteritems(), key=operator.itemgetter(1));
    d.reverse();

    return d;
