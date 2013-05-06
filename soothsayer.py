# -*- coding: utf-8 -*-
import os;
import subprocess;
import sys;
import time;
import multiprocessing;
import math;
import socket;
import random;
import collections;
import copy;

############### Functions ###################################

def command(command,piped = False):

    if piped:
        result = subprocess.Popen(command, shell=True,stdout=subprocess.PIPE).communicate()[0].decode();
    else:
        f = open('TiMBL_output','w');
        result = subprocess.Popen(command, shell=True,stdout=f,stderr=f);
        result.wait();

    return(result);

def get_character_function():
    """Return a function which gets a single char from the input"""

    try:
        #Windows variant

        import msvcrt

        def function():
            import msvcrt
            return msvcrt.getch().decode()

    except ImportError:
        #Unix variant

        def function():
            import sys, tty, termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch            

    return function;        

def clear():
    """Clears the screen""";

    os.system(['clear','cls'][os.name == 'nt']);

class Soothsayer():

    def __init__(self,approach = 'w', att_threshold=3, limit_personal_lexicon=3,
                 limit_backup_lexicon =30, test_cores = 10, punctuation = None,
                cut_file = '', close_server = '', recency_buffer = False, mode = ''):

        if punctuation is None:
            punctuation = ['.',',',':','!',';','?']

        self.approach       = approach;
        self.att_threshold  = att_threshold;
        self.limit_personal_lexicon = limit_personal_lexicon;
        self.limit_backup_lexicon   = limit_backup_lexicon;
        self.test_cores     = test_cores;
        self.cut_file       = cut_file;
        self.punctuation    = punctuation;

    def do_prediction(self,text,model,lexicon,recency_buffer,nr=''):
        """Returns a prediction by TiMBL and related info""";

        words = text.split();
        modelname = model.split('/')[1];

        if self.approach == 'w':

            if text == '' or text[-1] == ' ':

                #Figure out the left context and the word being worked on
                current_word = '';
                words = words[-3:];

                #Preprocessing for Timbl
                while len(words) < 3:
                    words = ['_'] + words;

                lcontext = ('c '+self.attenuate_string_simple(' '.join(words) + ' _',lexicon) + '\n').encode();
    #            lcontext = ('c ' + ' '.join(words) + ' _\n').encode();

                #Personal model
                self.sockets[0].sendall(lcontext);
                distr = '';

                while distr == '' or 'DISTRIBUTION' not in distr or distr[-1] != '\n':
                    try:
                        distr += self.sockets[0].recv(1024).decode();
                    except UnicodeError:
                        distr = 'DISTRIBUTION { de 0.999 }\n';
                        print('  Skipped one');

                final_distr = '[ word ]' + distr.split('DISTRIBUTION')[1];
                open('predictions/lcontext'+nr+'.'+modelname+'.IGTree.gr.out','w').write(final_distr);

                #General back-up model
                self.sockets[1].sendall(lcontext);
                distr = '';

                while distr == '' or 'DISTRIBUTION' not in distr or distr[-1] != '\n':
                    distr += self.sockets[1].recv(1024).decode();

                final_distr = '[ word ]' + distr.split('DISTRIBUTION')[1];
                open('predictions/lcontext'+nr+'.nlsave.IGTree.gr.out','w').write(final_distr);
                
            else:
                current_word = words[-1];
                words = words[-4:-1];

        elif self.approach == 'l':

            if text == '' or text[-1] == ' ':
                current_word = '';
            else:
                current_word = words[-1];

            #Preprocessing for Timbl
            newstring = text.replace(' ','_').replace('\n','');
            letters_before = ' '.join(newstring[-15:]);

            while len(letters_before) < 29:
                letters_before = '_ ' + letters_before;

            if len(current_word) > 0:
                letters_before = current_word[0] + letters_before[1:];

            lcontext = ('c '+ letters_before + ' _\n').encode();

            #Personal model
            self.sockets[0].sendall(lcontext);
            distr = '';

            while distr == '' or 'DISTRIBUTION' not in distr or distr[-1] != '\n':
                distr += self.sockets[0].recv(1024).decode();

            final_distr = '[ word ]' + distr.split('DISTRIBUTION')[1];
            open('predictions/lcontext'+nr+'.'+modelname+'.IGTree.gr.out','w').write(final_distr);

            #General back-up model
            self.sockets[1].sendall(lcontext);
            distr = '';

            while distr == '' or 'DISTRIBUTION' not in distr or distr[-1] != '\n':
                distr += self.sockets[1].recv(1024).decode();

            final_distr = '[ word ]' + distr.split('DISTRIBUTION')[1];
            open('predictions/lcontext'+nr+'.nl.IGTree.gr.out','w').write(final_distr);
        
                
        #Figure out how much has been typed so far
        boundary = len(current_word);

        #Standard vrs
        pick = '';
        second_pick = '';
        third_pick = '';
        predictions = [];
        used_rb = False;

        full_word = '';
        second_guess = '';
        third_guess = '';

        #Try context-sensitive, personal model
        if '' in [full_word,second_guess,third_guess]:
            pick, second_pick, third_pick, predictions, used_rb = self.read_prediction_file(modelname,nr,current_word,boundary);

            if used_rb:
                source += ' +RB';

            if full_word == '':
                full_word = pick;
                source = 'PERS. MODEL/IGTREE';
            if second_guess == '':
                second_guess = second_pick;
            if third_guess == '':
                third_guess = third_pick;

        #Try context-sensitive, general model
        if '' in [full_word,second_guess,third_guess]:
            pick, second_pick, third_pick, predictions,used_rb = self.read_prediction_file('nlsave',nr,current_word,boundary,recency_buffer);

            if used_rb:
                source += ' +RB';

            if full_word == '':
                full_word = pick;
                source = 'GEN. MODEL/IGTREE';
            if second_guess == '':
                second_guess = second_pick;
            if third_guess == '':
                third_guess = third_pick;

        #Try the recency_buffer
    #    if pick == '' and boundary > 0:
    #        source = 'RECENCY BUFFER';
    #        pick = read_recency_buffer(recency_buffer,current_word,boundary);

        #Try context-free, personal model
        if '' in [full_word,second_guess,third_guess]:
            pick,second_pick = self.read_frequency_file(model,current_word,boundary);

            if full_word == '':
                full_word = pick;
                source = 'PERS. MODEL/LEXICON';
            if second_guess == '':
                second_guess = second_pick;
            if third_guess == '':
                third_guess = third_pick;
            
        #Try context-free, general model
        if '' in [full_word,second_guess,third_guess]:
            pick,second_pick = self.read_frequency_file('wordmodels/nlsave',current_word,boundary);

            if full_word == '':
                full_word = pick;
                source = 'GEN. MODEL/LEXICON';
            if second_guess == '':
                second_guess = second_pick;
            if third_guess == '':
                third_guess = third_pick;

        #Admit that you don't know
        if full_word == '':
            source = 'I GIVE UP';

        #If it ends with punctuation, remove that
        elif full_word[-1] in self.punctuation:
            full_word = full_word[:-1];

        if len(second_guess) > 1 and second_guess[-1] in self.punctuation:
            second_guess = second_guess[:-1];

        if len(third_guess) > 1 and third_guess[-1] in self.punctuation:
            third_guess = third_guess[:-1];
        
        return {'full_word':full_word,'word_so_far':current_word,'nr_options':len(predictions),
                'second_guess':second_guess,'third_guess':third_guess, 'source': source}; 

    def read_prediction_file(self,modelname,nr,current_word,boundary,recency_buffer=False):
        """Reads and orders the predictions by TiMBL""";

        used_rb = False;

        #See if prediction is ready, if not wait
        ready = False;
                
        while not ready:
            try:
                raw_distr = open('predictions/lcontext'+nr+'.'+ modelname+'.IGTree.gr.out','r').read().split('] {');
                if len(raw_distr) > 1:
                    ready = True;
                else:
                    time.sleep(0.3);
            except IOError:
                time.sleep(0.3);

        #Turn prediction into list of tuples

        raw_distr = raw_distr[1];
        distr = raw_distr.strip()[:-2].split();

        last_word = None;
        predictions = [];
        for i in distr:

            if last_word == None:
                last_word = i;
            else:
                try:
                    predictions.append((last_word,float(i[:-1])));
                except ValueError:
                    pass;
                last_word = None;

        #Pick the best prediction, based on what has been typed so far
        pick = '';
        highest_confidence = 0;

        second_pick = '';
        second_highest_confidence = 0;

        third_pick = '';
        third_highest_confidence = 0;

        for i in predictions:
            if i[0] != '#DUMMY' and (i[0][:boundary] == current_word or self.approach == 'l'):
                if i[1] > highest_confidence:
                    third_pick = second_pick;
                    third_highest_confidence = second_highest_confidence;

                    second_pick = pick;
                    second_highest_confidence = highest_confidence;
                    
                    pick = i[0];
                    highest_confidence = i[1];
                elif i[1] > second_highest_confidence:
                    third_pick = second_pick;
                    third_highest_confidence = second_highest_confidence;

                    second_pick = i[0];
                    second_highest_confidence = i[1];                
                elif i[1] > third_highest_confidence:
                    third_pick = i[0];
                    third_highest_confidence = i[1];

    #    if settings['approach'] == 'l' and highest_confidence < 0.5:
    #        pick = '';
    #        second_pick = '';
    #    else:
    #        #Recency_buffer overrules with the word approach
    #        if recency_buffer:
    #            for i in recency_buffer:
    #                if i[:boundary] == current_word:
    #                    for j in predictions:
    #                        if i == j[0]:
    #                            if pick != i:
    #                                pick = i;
    #                                used_rb = True;
    #                            break;
                
        return pick, second_pick, third_pick, predictions, used_rb;

    def read_frequency_file(self,model,current_word,boundary):
        """Returns the most frequent word that starts with current_word"""

        pick = '';
        second_pick = '';
        lexicon = open(model+'.lex.txt');

        if len(current_word) == 0:
            return '','';
        
        for i in lexicon:
            if i[0] == current_word[0]: #quick check before you do more heavy stuff
                word, freq = i.split();
                if word[:boundary] == current_word:
                    if pick == '':
                        pick = word;
                    elif second_pick == '':
                        second_pick = word;
                        break;
                elif int(freq) < self.limit_backup_lexicon:
                    break;

        return pick,second_pick;

    def read_recency_buffer(self,rb,current_word,boundary):
        """Gets the latest word from the recency buffer that matches what you were typing""";

        for i in rb:
            if i[:boundary] == current_word:
                return i;
                break;

        return '';

    def start_servers(self,model,look_for_existing):
        """Starts the necessary servers and connects to them""";

        if self.approach == 'w':
            foldername = 'wordmodels';
            backupname = 'nlsave';
        elif self.approach == 'l':
            foldername = 'lettermodels';
            backupname = 'nlsmall';

        #Personal model
        succeeded = False;

        while not succeeded:

            if look_for_existing:
                port = get_port_for_timblserver(model+'.training.txt.IGTree');
            else:
                port = False;

            if not port:        
                port = get_free_port();
                command('timblserver -i '+model+'.training.txt.IGTree +vdb +D -a1 -G +vcf -S '+str(port)+' -C 1000');
                
            s1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM);

            try:
                s1.connect(('',port));
                s1.recv(1024);
                succeeded = True;
            except socket.error:
                pass;

        #General model
        succeeded = False;

        while not succeeded:

            if look_for_existing:
                port = get_port_for_timblserver(foldername+'/'+backupname+'.training.txt.IGTree');
            else:
                port = False;

            if not port:                
                port = get_free_port();
                command('timblserver -i '+foldername+'/'+backupname+'.training.txt.IGTree +vdb +D -a1 -G +vcf -S '+str(port)+' -C 1000');
                
            s2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM);

            try:
                s2.connect(('',port));
                s2.recv(1024);
                succeeded = True;
            except socket.error:
                pass;
        
        self.sockets = [s1,s2];

    def prepare_training_data(self,directory,make_testfile=False):

        if self.approach == 'w':
            foldername = 'wordmodels';
        elif self.approach == 'l':
            foldername = 'lettermodels';

        #Paste all texts in the directory into one string
        print('  Grab all files');
        files = os.listdir('input/'+directory);
        total_text = '';

        for n,i in enumerate(files):
            if n%1000 == 0:
                print('   ',n/len(files));

            content = open('input/'+directory+i,'r',encoding='utf-8',errors='ignore').read();

            if i == self.cut_file:
                words = content.split();
                boundary = round(len(words)*0.9);
                content = ' '.join(words[:boundary]);            
                print('   Cut file '+i);

            if self.approach == 'w':
                total_text += ' _ _ _ '+content;
            elif self.approach == 'l':
                total_text += ' ________________ '+open('input/'+directory+i,'r',encoding='utf-8',errors='ignore').read();

        #Tokenize
    #    total_text = ucto(total_text);

        #Create and load lexicon
        print('  Create lexicon');

        if make_testfile:
            lexicon_filename = foldername+'/'+directory[:-1]+'.90.lex.txt'; 
        else:
            lexicon_filename = foldername+'/'+directory[:-1]+'.lex.txt'; 
        self.string_to_lexicon(total_text,lexicon_filename);
        lexicon = self.load_lexicon(lexicon_filename);

        #In simulation mode, cut away 10 percent for testing later
        print('  Make test file if needed');
        if make_testfile:
            testfilename = foldername+'/'+directory[:-1]+'.10.test.txt';
            training_filename = foldername+'/'+directory[:-1]+'.90.training.txt';

            words = total_text.split();
            boundary = round(len(words)*0.9);

            open(testfilename,'w').write(' '.join(words[boundary:]));
            total_text = ' '.join(words[:boundary]);

        #In demo mode, just take all
        else:
            testfilename = '';
            training_filename = foldername+'/'+directory[:-1]+'.training.txt';

        #Attenuate the string with the training text
        print('  Attenuate string');
        total_text = self.attenuate_string_multicore(total_text,lexicon);

        #Make into ngrams, and save the file
        print('  Make ngrams');
        ngrams = self.make_ngrams(total_text);

        print('  Create file');
        training_file_content = '\n'.join(ngrams);
        open(training_filename,'w').write(training_file_content);

        #Return the filenames
        return training_filename, testfilename, lexicon;

    def make_ngrams(self,text):
        """Transforms a string into a list of 4-grams, using multiple cores""";

        result = multiprocessing.Queue();

        #Starts the workers
        def worker(nr,string,result):

            if self.approach == 'w':
                if nr == 0:
                    ngrams = window_string(string,True);
                else:
                    ngrams = window_string(string);
            elif self.approach == 'l':
                if nr == 0:
                    ngrams = window_string_letters(string,True);
                else:
                    ngrams = window_string_letters(string);

            result.put((nr,ngrams));

        if self.approach == 'w':
            substrings = divide_iterable(text.split(),10,3);
        elif self.approach == 'l':
            substrings = divide_iterable(text,10,15);    

        for n,i in enumerate(substrings):
            t = multiprocessing.Process(target=worker,args=[n,i,result]);
            t.start();

        #Wait until all results are in
        resultlist = [];

        while len(resultlist) < 10:

            while not result.empty():
                resultlist.append(result.get());

            time.sleep(1);

        #Sort and merge the results
        resultlist = sorted(resultlist,key=lambda x:x[0]);
        between_result = [x[1] for x in resultlist];    
        end_result = [];
        for i in between_result:
            end_result += i;

        return end_result;

    def train_model(self,filename):
        """Train a model on the basis of these ngrams""";

        command('timbl -f '+filename+' -I '+filename+'.IGTree +D +vdb -a1 -p 1000000',False);

        return filename.replace('.training.txt','');

    def string_to_lexicon(self,string,outputfilename):
        """Creates a lexicon from a string""";

        #Counts words
        words = string.replace('\n','').split();
        counts = {};

        for i in words:
            try:
                counts[i] += 1;
            except KeyError:
                counts[i] = 1;

        #Sort words, most frequent first
        counts = sorted(list(counts.items()),key=lambda x: x[1],reverse=True);

        #Save results
        lines = '';

        for i in counts:
            lines += i[0] + ' ' +str(i[1]) + '\n';

        open(outputfilename,'w').write(lines);

    def load_lexicon(self,filename):
        """Returns a list of all words more frequent than threshold""";

        lexicon = open(filename,'r');
        frequent_words = {};

        for i in lexicon:
            word,frequency = i.split();
            frequency = int(frequency);

            if frequency > self.att_threshold:
                try:
                    frequent_words[len(word)].append(word);
                except KeyError:
                    frequent_words[len(word)] = [word]

        return frequent_words;

    def attenuate_string_simple(self,string,lex):
        """Replaces infrequent words in string with #DUMMY, using one core""";

        words = string.split();
        result = '';

        for i in words:
            try:
                if i not in lex[len(i)]:
                    result += ' #DUMMY';
                else:
                    result += ' ' + i;
            except KeyError:
                result += ' #DUMMY';

        return result.strip();

    def attenuate_string_multicore(self,string,lex):
        """Replaces infrequent words in string with #DUMMY, using multiple cores""";

        #Prepare input and output
        words = string.split();
        word_nr = len(words);
        result = multiprocessing.Queue();

        #The actual work
        def dummify(n,word):        
            try:
                if not word in lex[len(word)] and word not in ['_']:
                    return '#DUMMY';
                else:
                    return word;

            except KeyError:
                return '#DUMMY';

        #Starts the workers
        def worker(nr,words,result):
            resultstring = '';
            wordtotal = len(words);

            for n,i in enumerate(words):
                
                resultstring += ' ' + dummify(n,i);

                #Report progress of the first worker
                if nr == 0 and n%100000 == 0:
                    print('  ',n / wordtotal);

            result.put((nr,resultstring));

        substrings = divide_iterable(words,10);
        
        for n,i in enumerate(substrings):
            t = multiprocessing.Process(target=worker,args=[n,i,result]);
            t.start();

        #Wait until all results are in
        resultlist = [];

        while len(resultlist) < 10:

            while not result.empty():
                resultlist.append(result.get());

            time.sleep(1);

        #Sort and merge the results
        resultlist = sorted(resultlist,key=lambda x:x[0]);
        actual_result = [x[1] for x in resultlist];
            
        return ' '.join(actual_result).strip();

    def attenuate_training_file(self,filename,lexicon):
        """Replaces infrequent words in trainingfile with #DUMMY""";

        f = open(filename,'r');

        newlines = [];
            
        for i in f:
            words = i.replace('\n','').split();
            result = '';
            
            for j in words[:-1]:
                if j not in lexicon and j not in ['_']:
                    result += ' #DUMMY';
                else:
                    result += ' '+j;

            result += ' '+words[-1];
            newlines.append(result.strip());

        open(filename,'w').write('\n'.join(newlines));

def add_prediction(text,text_colored,prediction,source):

    if text[-1] == ' ':
        text += prediction;
        text_colored += colors[source] + prediction + colors['white'];
        last_input = '';

    else:
        words = text.split();
        last_input = words[-1];        
        words = words[:-1];
        words.append(prediction);

        words_colored = text_colored.split();
        already_typed = words_colored[-1];
        words_colored = words_colored[:-1]
        prediction = already_typed + colors[source] + \
                     prediction[len(already_typed):] + colors['white'];
        words_colored.append(prediction);        

        text = ' '.join(words);
        text_colored = ' '.join(words_colored);
        
    return text, text_colored, last_input;
    
def demo_mode(model,lexicon,settings):

    #Start stuff needed for prediction
    recency_buffer = collections.deque(maxlen=settings['recency_buffer']);
    ss = Soothsayer(**settings);
    ss.start_servers(model,True);

    #Predict starting word
    prediction = ss.do_prediction('',model,lexicon,recency_buffer);

    #Ask for first char    
    print('Start typing whenever you want');
    get_character = get_character_function();

    #Start the process
    busy = True;
    text_so_far = '';
    text_so_far_colored = '';
    last_prediction = '';
    repeats = 0;

    while busy:
        rejected = False;
        char = str(get_character());

        #Accept prediction
        if char in [' ',')'] + settings['punctuation']:
            if prediction['full_word'] != '':
                text_so_far, text_so_far_colored, last_input = add_prediction(text_so_far,
                                                                              text_so_far_colored,
                                                                              prediction['full_word'],
                                                                              prediction['source']);
            text_so_far += char;
            text_so_far_colored += char;

            if char not in [' ',')']:
                text_so_far += ' ';
                text_so_far_colored += ' ';

            recency_buffer = add_to_recency_buffer(recency_buffer,text_so_far);

        #Reject prediction
        elif char == '\t':
            prediction = {'full_word': '', 'source':  'USER', 'second_guess': '', 'third_guess': '',
                          'nr_options': '', 'word_so_far': ''};
            rejected = True;

        #Hit backspace
        elif char == '\x7f':
            text_so_far = text_so_far[:-1];
            text_so_far_colored = text_so_far_colored[:-1];          

            while text_so_far_colored[-4:] in colors.values():
                text_so_far_colored = text_so_far_colored[:-4];

            while text_so_far_colored[-10:] in colors.values():
                text_so_far_colored = text_so_far_colored[:-10];

        #Don't accept prediction
        else:
            text_so_far += char;
            text_so_far_colored += char;

        #Predict new word
        if not rejected:
            prediction = ss.do_prediction(text_so_far,model,lexicon,recency_buffer);

        #Keep track of how often you did a prediction

        if last_prediction == prediction['full_word']:
            repeats += 1;
        else:
            repeats = 1;

        last_prediction = prediction['full_word'];

        #Show second best if you did a prediction too often
        if len(prediction['second_guess']) > 3 and repeats > 3:
            prediction['full_word'] = prediction['second_guess'];
            
        #Show the prediction
        clear();

        chars_typed = len(prediction['word_so_far']);
        print(text_so_far_colored+'|'+prediction['full_word'][chars_typed:]);
        print();
        print(prediction['second_guess']+', '+prediction['third_guess']+', '+ \
              str(prediction['nr_options'])+' options, source:',colors[prediction['source']],
              prediction['source'],colors['white']);

        #Check for quit
        if 'quit' in text_so_far.split():
            busy = False;

def simulation_mode(model,lexicon,testfile,settings):
    """Simulates someone typing, multicore""";

    result = multiprocessing.Queue();

    #Starts the workers
#    teststring = ucto(open(testfile,'r').read());
    teststring = ' ' + open(testfile,'r').read();
    substrings = divide_iterable(teststring.split(),settings['test_cores'],3);

    for n,i in enumerate(substrings):
        buffersize = settings['recency_buffer'];
        content_rb = substrings[n-1][-buffersize:];
        i = ' '.join(i);
        t = multiprocessing.Process(target=simulate,args=[model,lexicon,content_rb,i,settings,n,result]);
        t.start();

    #Wait until all results are in
    resultlist = [];

    while len(resultlist) < len(substrings):

        while not result.empty():
            resultlist.append(result.get());

        time.sleep(1);

    #Sort and merge the results
    resultlist = sorted(resultlist,key=lambda x:x[0]);
    between_result = [x[1:] for x in resultlist];    
    ks_saved_cks = 0;
    ks_saved_skks = 0;
    nr_ks = 0;
    duration = 0;
    end_result = '';
    
    for i in between_result:
        end_result += i[0];
        ks_saved_cks += i[1][0];
        ks_saved_skks += i[1][1];
        nr_ks += i[1][2];
        duration += i[1][3];

    end_result = 'Total CKS: '+str(ks_saved_cks/nr_ks)+'\n'+\
        'Total SKKS: '+str(ks_saved_skks/nr_ks)+'\n'+\
        'Total duration: '+str(duration)+'\n\n'+\
        end_result;
        
    open('output/Soothsayer_output','w').write(end_result);  

    print('Done');

def simulate(model,lexicon,content_rb,teststring,settings,nr,result):

    #Start the necessary things for the prediction
    recency_buffer = collections.deque(content_rb,settings['recency_buffer']);
    ss = Soothsayer(**settings);
    ss.start_servers(model,False);

    #Find out where to start (because of overlap)
    if nr == 0:
        starting_point = 0;
    else:
        first_words = teststring[:60].split()[:3];
        starting_point = len(first_words[0]) + len(first_words[1]) + len(first_words[2]) + 3;

    #Prepare vars and output
    starttime = time.time();
    total_keystrokes_saved = 0;
    total_keystrokes_saved_sk = 0; #Swiftkey measure
    already_predicted = False;
    skks_got_it_already = False;
    repeats = 1;
    last_prediction = '';

    output = '#############################\n##   CORE '+str(nr)+' STARTS HERE    ##\n#############################\n\n';

    #Go through the testfile letter for letter
    for i in range(starting_point,len(teststring)):

        if nr == 0 and i%10 == 0:
             print(i/len(teststring));

        #word finished
        if teststring[i] == ' ':
            skks_got_it_already = False;
            recency_buffer = add_to_recency_buffer(recency_buffer,teststring[:i]);

        #If the word was not already predicted, guess (again)
        if not already_predicted:

            #Figure out what has been said so far
            text_so_far = teststring[:i];
            nr_chars_typed = i - starting_point +1;

            #Do prediction
            prediction = ss.do_prediction(text_so_far,model,lexicon,recency_buffer,nr=str(nr));

            #Keep track of how often you did a prediction
            if last_prediction == prediction['full_word']:
                repeats += 1;
            else:
                repeats = 1;

            last_prediction = prediction['full_word'];

            #Show second best if you did a prediction too often
            if len(prediction['second_guess']) > 3 and repeats > 3:
                prediction['full_word'] = prediction['second_guess'];
                
            #Get and show what is written now
            current_word = find_current_word(teststring,i);

            if len(current_word) > 0 and current_word[-1] in settings['punctuation']:
                current_word = current_word[:-1];
                had_punc = True;
            else:
                had_punc = False;

            #If correct, calculate keystrokes saved and put in output            
            output += prediction['word_so_far']+', '+ current_word+', '+prediction['full_word']+'\n';
            if current_word == prediction['full_word']:
                
                output += '\n## FIRST GUESS CORRECT. SKIP. \n';

                keystrokes_saved = calculate_keystrokes_saved(prediction['word_so_far'],current_word);

                if had_punc:
                    keystrokes_saved += 1;
                    
                output += '## KEYSTROKES SAVED ' + str(keystrokes_saved)+' \n';

                total_keystrokes_saved += keystrokes_saved;
                perc = str(total_keystrokes_saved / nr_chars_typed);
                output += '## CKS ' + str(total_keystrokes_saved) + ' of ' + str(nr_chars_typed) + ' (' +perc+'%) \n';

                if not skks_got_it_already:
                    total_keystrokes_saved_sk += keystrokes_saved;            
                    perc = str(total_keystrokes_saved_sk / nr_chars_typed);
                    output += '## SKKS ' + str(total_keystrokes_saved_sk) + ' of ' + str(nr_chars_typed) + ' (' +perc+'%) \n';

                output += '## DURATION: '+str(time.time() - starttime)+' seconds \n\n';

                if teststring[i] != ' ':
                    already_predicted = True;

            elif not skks_got_it_already and current_word == prediction['second_guess']:
                output += '\n## SECOND GUESS CORRECT \n';

                keystrokes_saved = calculate_keystrokes_saved(prediction['word_so_far'],prediction['second_guess']);

                total_keystrokes_saved_sk += keystrokes_saved;            

                perc = str(total_keystrokes_saved_sk / nr_chars_typed);
                output += '## SKKS ' + str(total_keystrokes_saved_sk) + ' of ' + str(nr_chars_typed) + ' (' +perc+'%) \n\n';

                skks_got_it_already = True;

            elif teststring[i-1] == ' ' and current_word == prediction['third_guess']:
                output += '\n## THIRD GUESS CORRECT \n';

                keystrokes_saved = calculate_keystrokes_saved(prediction['word_so_far'],prediction['third_guess']);

                total_keystrokes_saved_sk += keystrokes_saved;            

                perc = str(total_keystrokes_saved_sk / nr_chars_typed);
                output += '## SKKS ' + str(total_keystrokes_saved_sk) + ' of ' + str(nr_chars_typed) + ' (' +perc+'%) \n\n';

                skks_got_it_already = True;
            else:
                pass;
                
        #Skip if the word was already predicted
        else:
            if teststring[i] == ' ':
                already_predicted = False;

    nr_chars_typed = len(teststring) - starting_point;

    output += '## FINAL CKS ' + str(total_keystrokes_saved) + ' of ' + str(nr_chars_typed) + '\n';
    output += '## FINAL SKKS ' + str(total_keystrokes_saved_sk) + ' of ' + str(nr_chars_typed) + '\n';
    output += '## FINAL DURATION: '+str(time.time() - starttime)+' seconds \n\n';

    results = [total_keystrokes_saved,total_keystrokes_saved_sk,len(text_so_far),time.time() - starttime];

    result.put((nr,output,results));          

def find_current_word(string, position):
    """Returns which word the user was typing at this position""";

    #If starting, just give the first word
    if position == 0:
        return string[:30].split()[0];

    #If not, do complicated stuff

    try:
        word = string[position-1];
    except IndexError:
        return '';

    separators = [' ','_'];

    #If starting with a space, give the next word
    while word in separators:
        try:
            position += 1;
            word = string[position-1];
        except IndexError:
            return '';

    c = 2;
    while word[0] not in separators and position-c > -1:
        word = string[position-c] + word;
        c += 1;

    c = 0;
    while word[-1] not in separators:
        try:
            word +=  string[position+c];
        except IndexError:
            break;
        c += 1;

    return word.strip();

def server_mode(settings):

    channels = {};
    channel_texts = {};
    channel_timbl = {};
    channel_lexicon = {};
    
    port = get_free_port();
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM);
    s.bind(('localhost',port));
    print('Started on port',port);

    print('Waiting for channel requests');
    busy = True;

    while busy:
        data, addr = s.recvfrom(1024);
        data = data.decode();
        mtype = data[0];
        message = data[1:];

        if mtype == 'R':
            print('Channel requested with model',message);

            #Look for a chanenl
            channel = find_free_channel(channels);
            channels[channel] = 'wordmodels/'+message;
            channel_texts[channel] = '';

            #Prepare predicting for this channel
            print('Starting servers and loading lexicon');
            channel_timbl[channel] = start_servers(channels[channel],settings);
            channel_lexicon[channel] = load_lexicon(channels[channel]+'.lex.txt');

            #Communicate the chosen channel            
            print('Using channel',channel);
            channel = str(channel);
            s.sendto(channel.encode(),addr);

        elif mtype == 'C':
            char = message[:-1];
            channel = int(message[-1]);
            channel_texts[channel] += char;
            prediction = do_prediction(channel_texts[channel],channels[channel],
                                 channel_lexicon[channel],'',settings,
                                 channel_timbl[channel]);            

            s.sendto(prediction['full_word'].encode(),addr);
            
def window_string(string,verbose = False):
    """Return the string as a list of 4-grams""";

    if not isinstance(string,list):
        words = string.split();
    else:
        words = string;

    word_nr = len(words);
    ngrams = [];
    
    for n,i in enumerate(range(0,len(words)-3)):
        ngrams.append(' '.join(words[i:i+4]));

    #Remove useless ones
    ngrams_to_remove = [];
    for n,i in enumerate(ngrams):
        if i[-1] == '_':
            ngrams_to_remove.append(i);

#    for i in ngrams_to_remove:
#        ngrams.remove(i);

    return ngrams;

def window_string_letters(string,verbose = False):
    """Return the string as a list of letter 15-grams""";

    words = string.split();
    newstring = string.replace(' ','_').replace('\n','');
    ngrams = [];
    
    for i in range(0,len(string)+1):

        current_word = find_current_word(newstring, i).replace('_','');
        letters_before = ' '.join(newstring[i-15:i]);
        if len(letters_before) > 1:
            if len(current_word) > 1 and letters_before[-1] != '_':
                letters_before = current_word[0] + letters_before[1:];
            else:
                letters_before = '_' + letters_before[1:];

            ngrams.append(letters_before + ' ' +current_word);

    #Remove useless ones
    ngrams_to_remove = [];
    for n,i in enumerate(ngrams):
        words = i.split();
        if i[-1] == '_' or len(words) != 16 or i == ngrams[-1]:
            ngrams_to_remove.append(i);

#    for i in ngrams_to_remove:
#        ngrams.remove(i);

    return ngrams[1:-1];

def calculate_keystrokes_saved(word_so_far,prediction):

    keystrokes_saved = len(prediction) - len(word_so_far);
    
    return keystrokes_saved;

def divide_iterable(it,n,overlap=None):
    """Returns any iterable into n pieces""";

    save_it = it;
    piece_size = math.ceil(len(it) / n);
    result = [];
    while len(it) > 0:
        result.append(it[:piece_size]);
        it = it[piece_size:];

    #If not enough pieces, divide the last piece
    if len(result) != n:
        last_piece = result[-1];
        boundary = round(len(last_piece)/2);
        result.append(last_piece[boundary:]);
        result[-2] = last_piece[:boundary];

    #Add overlap if needed
    if overlap:
        for n,i in enumerate(result):

            #Add left overlap
            pos = piece_size * n;
            result[n] = save_it[pos-overlap:pos] + result[n];

    return result;

def ucto(string):
    """Tokenizes a string with Ucto""";

    open('uctofile','w').write(string);
    result = command('ucto -L nl uctofile',True);
    os.remove('uctofile');
    return result.replace('<utt>','');

def get_free_port():
    
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM);
    s.bind(('',0));
    port = s.getsockname()[1];
    s.close();

    return int(port);

def get_port_for_timblserver(arg):
    import gettimbleserverport
    port = gettimbleserverport.getport(arg)

    if port == 0:
        print('  No server found, starting a new one');
        return False; 
    else:
        print('  Using running server');
        return port;

def add_to_recency_buffer(rb,text):
    """Adds the latest word in a string to the recency buffer""";

    last_word = text[-80:].split()[-1];
#    if len(last_word) < 6:
    if True:
        rb.appendleft(last_word);
    return rb

def find_free_channel(channels):
    """Finds a free channel, using the list of channels currently in use""";

    c = 0;
    found = False;

    while not found:
        try:
            channels[c];
            c += 1;
        except KeyError:
            found = True;

    return c;

######### Standalone code ######################

if __name__ == "__main__":

    #Colors
    colors = {'PERS. MODEL/IGTREE': '\033[0;35m', 'PERS. MODEL/LEXICON': '\033[1;34m',
              'GEN. MODEL/IGTREE': '\033[0;32m', 'GEN. MODEL/LEXICON': '\033[1;31m',
              'RECENCY BUFFER': '\033[1;31m', 'white': '\033[0m', 'I GIVE UP': '\033[0m',
              'USER': '\033[0m', 'PERS. MODEL/IGTREE +RB': '\033[1;31m',
              'GEN. MODEL/IGTREE +RB': '\033[1;31m'};

    # Static settings
    settings = {};
    settings['att_threshold'] = 3;
    settings['limit_personal_lexicon'] = 3;
    settings['limit_backup_lexicon'] = 30;
    settings['punctuation'] = ['.',',',':','!',';','?'];
    settings['test_cores'] = 10;

    #Figure out dynamic settings
    if '-d' in sys.argv:
        settings['mode'] = 'd';
    elif '-s' in sys.argv:
        settings['mode'] = 's';
    elif '-server' in sys.argv:
        settings['mode'] = 'server';
    else:
        settings['mode'] = input('Mode (d = demo, s = server): ');    

    if '-l' in sys.argv:
        settings['approach'] = 'l';
        modelfolder = 'lettermodels';
    elif '-w' in sys.argv:
        settings['approach'] = 'w';
        modelfolder = 'wordmodels';
    else:
        settings['approach'] = input('Approach (l = letter, w = word): ');

        if settings['approach'] == 'l':
            modelfolder = 'lettermodels';
        elif settings['approach'] == 'w':
            modelfolder = 'wordmodels';

    if '-id' in sys.argv:
        for n,i in enumerate(sys.argv):
            if i == '-id':
                inp = sys.argv[n+1] + '/';
    elif settings['mode'] != 'server':
        inp = input('Input directory: ') + '/';

    if '-tf' in sys.argv:
        for n,i in enumerate(sys.argv):
            if i == '-tf':
                testfile_preset = sys.argv[n+1];    
    else:
        testfile_preset = False;

    if '-rb' in sys.argv:
        for n,i in enumerate(sys.argv):
            if i == '-rb':
                settings['recency_buffer'] = int(sys.argv[n+1]);    
    else:
        settings['recency_buffer'] = 100;

    if '-dks' in sys.argv or '-dcs' in sys.argv:
        settings['close_server'] = False;
    else:
        settings['close_server'] = True;

    if '-cf' in sys.argv:
        for n,i in enumerate(sys.argv):
            if i == '-cf':
                settings['cut_file'] = sys.argv[n+1];    
    else:
        settings['cut_file'] = False;

    #Set directory reference (add .90 for the simulation mode)
    if settings['mode'] == 'd':
        dir_reference = inp[:-1];
    elif settings['mode'] == 's':
        dir_reference = inp[:-1] + '.90';

    #Try opening the language model (and testfile), or create one if it doesn't exist
    if settings['mode'] != 'server':

        ss = Soothsayer(**settings);

        try:
            open(modelfolder+'/'+dir_reference+'.training.txt','r');
            print('Loading existing model for '+dir_reference+'.');

            testfile = modelfolder+'/'+inp[:-1] + '.10.test.txt';
            model = modelfolder+'/'+dir_reference;
            lexicon = ss.load_lexicon(modelfolder+'/'+dir_reference+'.lex.txt');
        except IOError:
            print('Model not found. Prepare data to create a new one:');
            training_file, testfile, lexicon = ss.prepare_training_data(inp);
            print('Training model');
            model = ss.train_model(training_file);

    #If the user has his own testfile, abandon the automatically generated one
    if testfile_preset:
        testfile = testfile_preset;

    #Go do the prediction in one of the modes, with the model
    if settings['mode'] == 'd':
        demo_mode(model,lexicon,settings);
    elif settings['mode'] == 's':
        simulation_mode(model,lexicon,testfile,settings);
    elif settings['mode'] == 'server':
        server_mode(settings);

    #Close everything
    if settings['close_server']:
        command('killall timblserver');

#TODO
# Server modus
# Mogelijk: werkt het beter als je na lang doorgaan stopt met suggereren?
# Lettermodus: gaat er ergens iets fout?
# Haakje sluiten in simulatiemodus
# Backspace: fout als je over de kleurgrenzen heen backspacet gaan de kleuren raar doen
