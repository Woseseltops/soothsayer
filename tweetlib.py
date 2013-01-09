import twython as t

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

def is_dutch(tweet):
    """Returns whether a tweet is Dutch or not""";

    words = clean_tweet(tweet).split();

    #Half of the words should be in the list
    amount_dutch_threshold = round(len(words) / 2);

    #Import the list
    word_list = get_dutch_wordlist();

    #See how much words are in the list
    found_in_list = 0;

    for i in words:
        if i in word_list:
            found_in_list += 1;

    #Enough words Dutch? Return true
    if found_in_list >= amount_dutch_threshold:
        return True;
    else:
        return False;

def get_dutch_wordlist():
    """Returns a list of the most frequent Dutch words""";

    lines = open('nl.txt','r').readlines();
    words = [];

    for i in lines:
        word,frequency = i.split(' ');
        word = word.strip();
        frequency = int(frequency);

        if frequency > 200:
            words.append(word);
    
    return(words);

def get_most_mentioned_addressees():
    """WIP""";

    #If this tweet contains addressees we don't know yet, and the tweet is Dutch,
    #add them to the people we follow
    addressees = tweetlib.get_addressees(tweet[1]);            

    if len(addressees) > 0 and tweetlib.is_dutch(tweet[1]):
        tweeterfile = open(tweeterfile_loc,'a');
        
        for addressee in addressees:                    
            if addressee not in tweeters:                    
                tweeterfile.write(addressee+'\n');
                tweeters.append(addressee);

