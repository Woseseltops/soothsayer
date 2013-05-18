import soothsayer
import soothsayer.terminal
import sys
import collections
import os
import multiprocessing
import math
import time

def demo_mode(model,lexicon,settings):

    #Start stuff needed for prediction
    recency_buffer = collections.deque(maxlen=settings['recency_buffer'])
    ss = soothsayer.Soothsayer(**settings)
    ss.start_servers(model,True)
    ss.setup_basic_modules(model)

    #Predict starting word
    prediction = ss.do_prediction('',lexicon,recency_buffer)

    #Ask for first char    
    print('Start typing whenever you want')
    get_character = soothsayer.terminal.get_character_function()

    #Start the process
    colors = soothsayer.terminal.colors
    text_so_far = ''
    text_so_far_colored = ''
    last_prediction = ''
    repeats = 0

    while True:
        rejected = False
        char = str(get_character())

        #Accept prediction
        if char in [' ',')'] + settings['punctuation']:
            if prediction['full_word'] != '':
                text_so_far, text_so_far_colored, last_input = add_prediction(text_so_far,
                                                                              text_so_far_colored,
                                                                              prediction['full_word'],
                                                                              prediction['source'])
            text_so_far += char
            text_so_far_colored += char

            if char not in [' ',')']:
                text_so_far += ' '
                text_so_far_colored += ' '

            recency_buffer = add_to_recency_buffer(recency_buffer,text_so_far)

        #Reject prediction
        elif char == '\t':
            prediction = {'full_word': '', 'source':  'USER', 'second_guess': '', 'third_guess': '',
                          'nr_options': '', 'word_so_far': ''}
            rejected = True

        #Hit backspace
        elif char == '\x7f':
            text_so_far = text_so_far[:-1]
            text_so_far_colored = text_so_far_colored[:-1]          

            while text_so_far_colored[-4:] in colors.values():
                text_so_far_colored = text_so_far_colored[:-4]

            while text_so_far_colored[-10:] in colors.values():
                text_so_far_colored = text_so_far_colored[:-10]

        #Don't accept prediction
        else:
            text_so_far += char
            text_so_far_colored += char

        #Predict new word
        if not rejected:
            prediction = ss.do_prediction(text_so_far,lexicon,recency_buffer)

        #Keep track of how often you did a prediction

        if last_prediction == prediction['full_word']:
            repeats += 1
        else:
            repeats = 1

        last_prediction = prediction['full_word']

        #Show second best if you did a prediction too often
        if len(prediction['second_guess']) > 3 and repeats > 3:
            prediction['full_word'] = prediction['second_guess']
            
        #Show the prediction
        soothsayer.terminal.clear()

        chars_typed = len(prediction['word_so_far'])
        print(text_so_far_colored+'|'+prediction['full_word'][chars_typed:])
        print()
        print(prediction['second_guess']+', '+prediction['third_guess']+', '+ \
              str(prediction['nr_options'])+' options, source:',colors[prediction['source']],
              prediction['source'],colors['white'])

        #Check for quit
        if 'quit' in text_so_far.split():
            break;

def add_prediction(text,text_colored,prediction,source):

    colors = soothsayer.terminal.colors;

    if text[-1] == ' ':
        text += prediction
        text_colored += colors[source] + prediction + colors['white']
        last_input = ''

    else:
        words = text.split()
        last_input = words[-1]        
        words = words[:-1]
        words.append(prediction)

        words_colored = text_colored.split()
        already_typed = words_colored[-1]
        words_colored = words_colored[:-1]
        prediction = already_typed + colors[source] + \
                     prediction[len(already_typed):] + colors['white']
        words_colored.append(prediction)        

        text = ' '.join(words)
        text_colored = ' '.join(words_colored)
        
    return text, text_colored, last_input
    

def simulation_mode(model,lexicon,testfile,settings):
    """Simulates someone typing, multicore"""

    result = multiprocessing.Queue()

    #Starts the workers
#    teststring = ucto(open(testfile,'r').read())
    teststring = ' ' + open(testfile,'r').read()
    substrings = divide_iterable(teststring.split(),settings['test_cores'],3)

    for n,i in enumerate(substrings):
        buffersize = settings['recency_buffer']
        content_rb = substrings[n-1][-buffersize:]
        i = ' '.join(i)
        t = multiprocessing.Process(target=simulate,args=[model,lexicon,content_rb,i,settings,n,result])
        t.start()

    #Wait until all results are in
    resultlist = []

    while len(resultlist) < len(substrings):

        while not result.empty():
            resultlist.append(result.get())

        time.sleep(1)

    #Sort and merge the results
    resultlist = sorted(resultlist,key=lambda x:x[0])
    between_result = [x[1:] for x in resultlist]    
    ks_saved_cks = 0
    ks_saved_skks = 0
    nr_ks = 0
    duration = 0
    end_result = ''
    
    for i in between_result:
        end_result += i[0]
        ks_saved_cks += i[1][0]
        ks_saved_skks += i[1][1]
        nr_ks += i[1][2]
        duration += i[1][3]

    end_result = 'Total CKS: '+str(ks_saved_cks/nr_ks)+'\n'+\
        'Total SKKS: '+str(ks_saved_skks/nr_ks)+'\n'+\
        'Total duration: '+str(duration)+'\n\n'+\
        end_result
        
    open('output/Soothsayer_output','w').write(end_result)  

    print('Done')

def simulate(model,lexicon,content_rb,teststring,settings,nr,result):

    #Start the necessary things for the prediction
    recency_buffer = collections.deque(content_rb,settings['recency_buffer'])
    ss = soothsayer.Soothsayer(**settings)    
    ss.start_servers(model,False)
    ss.setup_basic_modules(model)

    #Find out where to start (because of overlap)
    if nr == 0:
        starting_point = 0
    else:
        first_words = teststring[:60].split()[:3]
        starting_point = len(first_words[0]) + len(first_words[1]) + len(first_words[2]) + 3

    #Prepare vars and output
    starttime = time.time()
    total_keystrokes_saved = 0
    total_keystrokes_saved_sk = 0 #Swiftkey measure
    already_predicted = False
    skks_got_it_already = False
    repeats = 1
    last_prediction = ''

    output = '#############################\n##   CORE '+str(nr)+' STARTS HERE    ##\n#############################\n\n'

    #Go through the testfile letter for letter
    for i in range(starting_point,len(teststring)):

        if nr == 0 and i%10 == 0:
             print(i/len(teststring))

        #word finished
        if teststring[i] == ' ':
            skks_got_it_already = False
            recency_buffer = add_to_recency_buffer(recency_buffer,teststring[:i])

        #If the word was not already predicted, guess (again)
        if not already_predicted:

            #Figure out what has been said so far
            text_so_far = teststring[:i]
            nr_chars_typed = i - starting_point +1

            #Do prediction
            prediction = ss.do_prediction(text_so_far,lexicon,recency_buffer,nr=str(nr))

            #Keep track of how often you did a prediction
            if last_prediction == prediction['full_word']:
                repeats += 1
            else:
                repeats = 1

            last_prediction = prediction['full_word']

            #Show second best if you did a prediction too often
#            if len(prediction['second_guess']) > 1 and repeats > 1:
#                prediction['full_word'] = prediction['second_guess']
                
            #Get and show what is written now
            current_word = find_current_word(teststring,i)

            if len(current_word) > 0 and current_word[-1] in settings['punctuation']:
                current_word = current_word[:-1]
                had_punc = True
            else:
                had_punc = False

            #If correct, calculate keystrokes saved and put in output            
            output += prediction['word_so_far']+', '+ current_word+', '+prediction['full_word']+'\n'
            if current_word == prediction['full_word']:
                
                output += '\n## FIRST GUESS CORRECT. SKIP. \n'

                keystrokes_saved = calculate_keystrokes_saved(prediction['word_so_far'],current_word)

                if had_punc:
                    keystrokes_saved += 1
                    
                output += '## KEYSTROKES SAVED ' + str(keystrokes_saved)+' \n'

                total_keystrokes_saved += keystrokes_saved
                perc = str(total_keystrokes_saved / nr_chars_typed)
                output += '## CKS ' + str(total_keystrokes_saved) + ' of ' + str(nr_chars_typed) + ' (' +perc+'%) \n'

                if not skks_got_it_already:
                    total_keystrokes_saved_sk += keystrokes_saved            
                    perc = str(total_keystrokes_saved_sk / nr_chars_typed)
                    output += '## SKKS ' + str(total_keystrokes_saved_sk) + ' of ' + str(nr_chars_typed) + ' (' +perc+'%) \n'

                output += '## DURATION: '+str(time.time() - starttime)+' seconds \n\n'

                if teststring[i] != ' ':
                    already_predicted = True

            elif not skks_got_it_already and current_word == prediction['second_guess']:
                output += '\n## SECOND GUESS CORRECT \n'

                keystrokes_saved = calculate_keystrokes_saved(prediction['word_so_far'],prediction['second_guess'])

                total_keystrokes_saved_sk += keystrokes_saved            

                perc = str(total_keystrokes_saved_sk / nr_chars_typed)
                output += '## SKKS ' + str(total_keystrokes_saved_sk) + ' of ' + str(nr_chars_typed) + ' (' +perc+'%) \n\n'

                skks_got_it_already = True

            elif teststring[i-1] == ' ' and current_word == prediction['third_guess']:
                output += '\n## THIRD GUESS CORRECT \n'

                keystrokes_saved = calculate_keystrokes_saved(prediction['word_so_far'],prediction['third_guess'])

                total_keystrokes_saved_sk += keystrokes_saved            

                perc = str(total_keystrokes_saved_sk / nr_chars_typed)
                output += '## SKKS ' + str(total_keystrokes_saved_sk) + ' of ' + str(nr_chars_typed) + ' (' +perc+'%) \n\n'

                skks_got_it_already = True
            else:
                pass
                
        #Skip if the word was already predicted
        else:
            if teststring[i] == ' ':
                already_predicted = False

    nr_chars_typed = len(teststring) - starting_point

    output += '## FINAL CKS ' + str(total_keystrokes_saved) + ' of ' + str(nr_chars_typed) + '\n'
    output += '## FINAL SKKS ' + str(total_keystrokes_saved_sk) + ' of ' + str(nr_chars_typed) + '\n'
    output += '## FINAL DURATION: '+str(time.time() - starttime)+' seconds \n\n'

    results = [total_keystrokes_saved,total_keystrokes_saved_sk,len(text_so_far),time.time() - starttime]

    result.put((nr,output,results))          

def find_current_word(string, position):
    """Returns which word the user was typing at this position"""

    #If starting, just give the first word
    if position == 0:
        return string[:30].split()[0]

    #If not, do complicated stuff

    try:
        word = string[position-1]
    except IndexError:
        return ''

    separators = [' ','_']

    #If starting with a space, give the next word
    while word in separators:
        try:
            position += 1
            word = string[position-1]
        except IndexError:
            return ''

    c = 2
    while word[0] not in separators and position-c > -1:
        word = string[position-c] + word
        c += 1

    c = 0
    while word[-1] not in separators:
        try:
            word +=  string[position+c]
        except IndexError:
            break
        c += 1

    return word.strip()

def server_mode(settings):

    channels = {}
    channel_texts = {}
    channel_timbl = {}
    channel_lexicon = {}
    
    port = get_free_port()
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.bind(('localhost',port))
    print('Started on port',port)

    print('Waiting for channel requests')

    while True:
        data, addr = s.recvfrom(1024)
        data = data.decode()
        mtype = data[0]
        message = data[1:]

        if mtype == 'R':
            print('Channel requested with model',message)

            #Look for a chanenl
            channel = find_free_channel(channels)
            channels[channel] = 'wordmodels/'+message
            channel_texts[channel] = ''

            #Prepare predicting for this channel
            print('Starting servers and loading lexicon')
            channel_timbl[channel] = start_servers(channels[channel],settings)
            channel_lexicon[channel] = load_lexicon(channels[channel]+'.lex.txt')

            #Communicate the chosen channel            
            print('Using channel',channel)
            channel = str(channel)
            s.sendto(channel.encode(),addr)

        elif mtype == 'C':
            char = message[:-1]
            channel = int(message[-1])
            channel_texts[channel] += char
            prediction = do_prediction(channel_texts[channel],channels[channel],
                                 channel_lexicon[channel],'',settings,
                                 channel_timbl[channel])            

            s.sendto(prediction['full_word'].encode(),addr)

def httpserver_mode(settings):

    import cherrypy

    class httpserver(object):

        def index(self):
            return "<h1>Hello!</h1>"
        index.exposed = True

        def predict(self,text,model):
            return 'Sending '+text+' to '+model
        predict.exposed = True

        def load_model(self,model):
            return 'Starting '+model
        load_model.exposed = True
            
    cherrypy.config.update({
            'server.socket_host': '0.0.0.0',
            'server.socket_port': 4431
        })

    cherrypy.quickstart(httpserver())
            
def window_string(string,verbose = False):
    """Return the string as a list of 4-grams"""

    if not isinstance(string,list):
        words = string.split()
    else:
        words = string

    word_nr = len(words)
    ngrams = []
    
    for n,i in enumerate(range(0,len(words)-3)):
        ngrams.append(' '.join(words[i:i+4]))

    #Remove useless ones
    ngrams_to_remove = []
    for n,i in enumerate(ngrams):
        if i[-1] == '_':
            ngrams_to_remove.append(i)

#    for i in ngrams_to_remove:
#        ngrams.remove(i)

    return ngrams

def window_string_letters(string,verbose = False):
    """Return the string as a list of letter 15-grams"""

    words = string.split()
    newstring = string.replace(' ','_').replace('\n','')
    ngrams = []
    
    for i in range(0,len(string)+1):

        current_word = find_current_word(newstring, i).replace('_','')
        letters_before = ' '.join(newstring[i-15:i])
        if len(letters_before) > 1:
            if len(current_word) > 1 and letters_before[-1] != '_':
                letters_before = current_word[0] + letters_before[1:]
            else:
                letters_before = '_' + letters_before[1:]

            ngrams.append(letters_before + ' ' +current_word)

    #Remove useless ones
    ngrams_to_remove = []
    for n,i in enumerate(ngrams):
        words = i.split()
        if i[-1] == '_' or len(words) != 16 or i == ngrams[-1]:
            ngrams_to_remove.append(i)

#    for i in ngrams_to_remove:
#        ngrams.remove(i)

    return ngrams[1:-1]

def calculate_keystrokes_saved(word_so_far,prediction):

    keystrokes_saved = len(prediction) - len(word_so_far)
    
    return keystrokes_saved

def divide_iterable(it,n,overlap=None):
    """Returns any iterable into n pieces"""

    save_it = it
    piece_size = math.ceil(len(it) / n)
    result = []
    while len(it) > 0:
        result.append(it[:piece_size])
        it = it[piece_size:]

    #If not enough pieces, divide the last piece
    if len(result) != n:
        last_piece = result[-1]
        boundary = round(len(last_piece)/2)
        result.append(last_piece[boundary:])
        result[-2] = last_piece[:boundary]

    #Add overlap if needed
    if overlap:
        for n,i in enumerate(result):

            #Add left overlap
            pos = piece_size * n
            result[n] = save_it[pos-overlap:pos] + result[n]

    return result

def ucto(string):
    """Tokenizes a string with Ucto"""

    open('uctofile','w').write(string)
    result = command('ucto -L nl uctofile',True)
    os.remove('uctofile')
    return result.replace('<utt>','')

def add_to_recency_buffer(rb,text):
    """Adds the latest word in a string to the recency buffer"""

    last_word = text[-80:].split()[-1]
#    if len(last_word) < 6:
    if True:
        rb.appendleft(last_word)
    return rb

def find_free_channel(channels):
    """Finds a free channel, using the list of channels currently in use"""

    c = 0
    found = False

    while not found:
        try:
            channels[c]
            c += 1
        except KeyError:
            found = True

    return c

#=========== Script starts here ==============

# Static settings
settings = {}
settings['att_threshold'] = 3
settings['limit_personal_lexicon'] = 3
settings['limit_backup_lexicon'] = 30
settings['punctuation'] = ['.',',',':','!','','?']
settings['test_cores'] = 10

#Figure out dynamic settings
if '-d' in sys.argv:
    settings['mode'] = 'd'
elif '-s' in sys.argv:
    settings['mode'] = 's'
elif '-server' in sys.argv:
    settings['mode'] = 'server'
else:
    settings['mode'] = input('Mode (d = demo, s = server): ')    

if '-l' in sys.argv:
    settings['approach'] = 'l'
    modelfolder = 'lettermodels'
elif '-w' in sys.argv:
    settings['approach'] = 'w'
    modelfolder = 'wordmodels'
else:
    settings['approach'] = input('Approach (l = letter, w = word): ')

    if settings['approach'] == 'l':
        modelfolder = 'lettermodels'
    elif settings['approach'] == 'w':
        modelfolder = 'wordmodels'

if '-id' in sys.argv:
    i = sys.argv.index('-id')
    inp = sys.argv[i+1] + '/'
elif settings['mode'] != 'server':
    inp = input('Input directory: ') + '/'

if '-tf' in sys.argv:
    i = sys.argv.index('-tf')
    testfile_preset = sys.argv[i+1]
else:
    testfile_preset = False

if '-rb' in sys.argv:
    i = sys.argv.index('-rb')
    settings['recency_buffer'] = int(sys.argv[i+1])
else:
    settings['recency_buffer'] = 100

if '-dks' in sys.argv or '-dcs' in sys.argv:
    settings['close_server'] = False
else:
    settings['close_server'] = True

if '-cf' in sys.argv:
    i = sys.argv.index('-cf')
    settings['cut_file'] = sys.argv[i+1]
else:
    settings['cut_file'] = False
    
#Set directory reference (add .90 for the simulation mode)
if settings['mode'] == 'd':
    dir_reference = inp[:-1]
elif settings['mode'] == 's':
    dir_reference = inp[:-1] + '.90'

#Try opening the language model (and testfile), or create one if it doesn't exist
if settings['mode'] in ['s','d']:

    ss = soothsayer.Soothsayer(**settings)

    try:
        open(modelfolder+'/'+dir_reference+'.training.txt','r')
        print('Loading existing model for '+dir_reference+'.')

        testfile = modelfolder+'/'+inp[:-1] + '.10.test.txt'
        model = modelfolder+'/'+dir_reference
        lexicon = ss.load_lexicon(modelfolder+'/'+dir_reference+'.lex.txt')
    except IOError:
        print('Model not found. Prepare data to create a new one:')
        training_file, testfile, lexicon = ss.prepare_training_data(inp)
        print('Training model')
        model = ss.train_model(training_file)

#If the user has his own testfile, abandon the automatically generated one
if testfile_preset:
    testfile = testfile_preset

#Go do the prediction in one of the modes, with the model
if settings['mode'] == 'd':
    demo_mode(model,lexicon,settings)
elif settings['mode'] == 's':
    simulation_mode(model,lexicon,testfile,settings)
elif settings['mode'] == 'server':
    server_mode(settings)
elif settings['mode'] == 'httpserver':
    httpserver_mode(settings)

#Close everything
if settings['close_server']:
    soothsayer.command('killall timblserver')
