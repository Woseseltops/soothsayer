# -*- coding: utf-8 -*-
import os
import subprocess
import sys
import time
import multiprocessing
import math
import socket
import random
import collections
import copy
import soothsayer.timbl

############### Functions ###################################

def command(command,piped = False):

    if piped:
        result = subprocess.Popen(command, shell=True,stdout=subprocess.PIPE).communicate()[0].decode()
    else:
        f = open('TiMBL_output','w')
        result = subprocess.Popen(command, shell=True,stdout=f,stderr=f)
        result.wait()

    return(result)

class Soothsayer():

    def __init__(self,approach = 'w', att_threshold=3, limit_personal_lexicon=3,
                 limit_backup_lexicon =30, test_cores = 10, punctuation = None,
                cut_file = '', close_server = True, recency_buffer = False, mode = '',
                 port = 0):

        self.approach       =   approach
        self.att_threshold  =   att_threshold
        self.test_cores     =   test_cores
        self.cut_file       =   cut_file
        self.limit_personal_lexicon = limit_personal_lexicon
        self.limit_backup_lexicon   = limit_backup_lexicon

        if punctuation == None:
            self.punctuation = ['.',',',':','!','','?']
        else:
            self.punctuation = punctuation

        self.port = port
        self.close_server   =   close_server

        self.modules = []
        self.timblservers = {}

    def setup_basic_modules(self,model):
    
        self.modules = [Module(self,'PERS. MODEL/IGTREE',model.name,'igtree'),
                        Module(self,'GEN. MODEL/IGTREE','nlsave','igtree'),
                        Module(self,'PERS. MODEL/LEXICON',model.name,'lex'),
                        Module(self,'GEN. MODEL/LEXICON','nlsave','lex'),
                        ]

    def do_prediction(self,text,lexicon,recency_buffer,nr=''):
        """Returns a prediction by TiMBL and related info"""

        words = text.split()

        if self.approach == 'w':

            if text == '' or text[-1] == ' ':

                #Figure out the left context and the word being worked on
                current_word = ''
                words = words[-3:]

                #Preprocessing for Timbl
                while len(words) < 3:
                    words = ['_'] + words

                lcontext = ('c '+self.attenuate_string_simple(' '.join(words) + ' _',lexicon) + '\n').encode()
    #            lcontext = ('c ' + ' '.join(words) + ' _\n').encode()

                #Communicate with Timbl
                for i in self.modules:
                    if i.kind == 'igtree':
                        i.send_to_your_server(lcontext,nr);                
            else:
                current_word = words[-1]
                words = words[-4:-1]

        elif self.approach == 'l':

            if text == '' or text[-1] == ' ':
                current_word = ''
            else:
                current_word = words[-1]

            #Preprocessing for Timbl
            newstring = text.replace(' ','_').replace('\n','')
            letters_before = ' '.join(newstring[-15:])

            while len(letters_before) < 29:
                letters_before = '_ ' + letters_before

            if len(current_word) > 0:
                letters_before = current_word[0] + letters_before[1:]

            lcontext = ('c '+ letters_before + ' _\n').encode()

            #Personal model
            self.sockets[0].sendall(lcontext)
            distr = ''

            while distr == '' or 'DISTRIBUTION' not in distr or distr[-1] != '\n':
                distr += self.sockets[0].recv(1024).decode()

            final_distr = '[ word ]' + distr.split('DISTRIBUTION')[1]
            open('predictions/lcontext'+nr+'.'+modelname+'.IGTree.gr.out','w').write(final_distr)

            #General back-up model
            self.sockets[1].sendall(lcontext)
            distr = ''

            while distr == '' or 'DISTRIBUTION' not in distr or distr[-1] != '\n':
                distr += self.sockets[1].recv(1024).decode()

            final_distr = '[ word ]' + distr.split('DISTRIBUTION')[1]
            open('predictions/lcontext'+nr+'.nl.IGTree.gr.out','w').write(final_distr)
        
                
        #Figure out how much has been typed so far
        boundary = len(current_word)

        #Standard vrs
        pick = ''
        second_pick = ''
        third_pick = ''
        predictions = []

        full_word = ''
        second_guess = ''
        third_guess = ''

        for i in self.modules:

            pick, second_pick, third_pick, predictions = i.run(current_word,boundary,nr)

            if full_word == '':
                full_word = pick
                source = i.name
            if second_guess == '':
                second_guess = second_pick
            if third_guess == '':
                third_guess = third_pick

            if '' not in [full_word,second_guess,third_guess]:
                break

        #Admit that you don't know
        if full_word == '':
            source = 'I GIVE UP'

        #If it ends with punctuation, remove that
        elif full_word[-1] in self.punctuation:
            full_word = full_word[:-1]

        if len(second_guess) > 1 and second_guess[-1] in self.punctuation:
            second_guess = second_guess[:-1]

        if len(third_guess) > 1 and third_guess[-1] in self.punctuation:
            third_guess = third_guess[:-1]
        
        return {'full_word':full_word,'word_so_far':current_word,'nr_options':len(predictions),
                'second_guess':second_guess,'third_guess':third_guess, 'source': source} 

    def read_prediction_file(self,modelname,nr,current_word,boundary):
        """Reads and orders the predictions by TiMBL"""

        #See if prediction is ready, if not wait
        ready = False
                
        while not ready:
            try:
                raw_distr = open('predictions/lcontext'+nr+'.'+ modelname+'.IGTree.gr.out','r').read().split('] {')
                if len(raw_distr) > 1:
                    ready = True
                else:
                    time.sleep(0.3)
            except IOError:
                time.sleep(0.3)

        #Turn prediction into list of tuples

        raw_distr = raw_distr[1]
        distr = raw_distr.strip()[:-2].split()

        last_word = None
        predictions = []
        for i in distr:

            if last_word == None:
                last_word = i
            else:
                try:
                    predictions.append((last_word,float(i[:-1])))
                except ValueError:
                    pass
                last_word = None

        #Pick the best prediction, based on what has been typed so far
        pick = ''
        highest_confidence = 0

        second_pick = ''
        second_highest_confidence = 0

        third_pick = ''
        third_highest_confidence = 0

        for i in predictions:
            if i[0] != '#DUMMY' and (i[0][:boundary] == current_word or self.approach == 'l'):
                if i[1] > highest_confidence:
                    third_pick = second_pick
                    third_highest_confidence = second_highest_confidence

                    second_pick = pick
                    second_highest_confidence = highest_confidence
                    
                    pick = i[0]
                    highest_confidence = i[1]
                elif i[1] > second_highest_confidence:
                    third_pick = second_pick
                    third_highest_confidence = second_highest_confidence

                    second_pick = i[0]
                    second_highest_confidence = i[1]                
                elif i[1] > third_highest_confidence:
                    third_pick = i[0]
                    third_highest_confidence = i[1]
                
        return pick, second_pick, third_pick, predictions

    def read_frequency_file(self,model,current_word,boundary):
        """Returns the most frequent word that starts with current_word"""

        pick = ''
        second_pick = ''
        lexicon = open('wordmodels/'+model+'.lex.txt')

        if len(current_word) == 0:
            return '',''
        
        for i in lexicon:
            if i[0] == current_word[0]: #quick check before you do more heavy stuff
                word, freq = i.split()
                if word[:boundary] == current_word:
                    if pick == '':
                        pick = word
                    elif second_pick == '':
                        second_pick = word
                        break
                elif int(freq) < self.limit_backup_lexicon:
                    break

        return pick,second_pick

    def only_one_word_possible(self,model,current_word,boundary):
        """Returns the most frequent word that starts with current_word"""

        pick = ''
        lexicon = open(model+'.lex.txt')

        if len(current_word) == 0:
            return ''
        
        for i in lexicon:
            if i[0] == current_word[0]: #quick check before you do more heavy stuff
                word, freq = i.split()
                if word[:boundary] == current_word:
                    if pick == '':
                        pick = word
                    else:
                        return ''

        return pick

    def read_recency_buffer(self,rb,current_word,boundary):
        """Gets the latest word from the recency buffer that matches what you were typing"""

        for i in rb:
            if i[:boundary] == current_word:
                return i
                break

        return ''

    def start_servers(self,models,look_for_existing):
        """Starts the necessary servers and connects to them"""

        for i in models:
            t = timbl.Timbl()

            if not self.close_server:
                t.neverkillserver = True

            while True:

                if look_for_existing:
                    port = t.findport(i.location)
                    
                else:
                    port = False

                if port:
                    print('Connecting to an existing server running',i.name)
                    t.neverkillserver = True
                else:
                    port = t.start_server(i.location)
                    print('No server found. Started a new server running',i.name)
        
                if t.connect(port):
                    break;
                else:
                    print('No connect');

            self.timblservers[i.name] = t 

    def prepare_training_data(self,directory,make_testfile=False):

        if self.approach == 'w':
            foldername = 'wordmodels'
        elif self.approach == 'l':
            foldername = 'lettermodels'

        #Paste all texts in the directory into one string
        print('  Grab all files')
        files = os.listdir('input/'+directory)
        total_text = ''

        for n,i in enumerate(files):
            if n%1000 == 0:
                print('   ',n/len(files))

            content = open('input/'+directory+i,'r',encoding='utf-8',errors='ignore').read()

            if i == self.cut_file:
                words = content.split()
                boundary = round(len(words)*0.9)
                content = ' '.join(words[:boundary])            
                print('   Cut file '+i)

            if self.approach == 'w':
                total_text += ' _ _ _ '+content
            elif self.approach == 'l':
                total_text += ' ________________ '+open('input/'+directory+i,'r',encoding='utf-8',errors='ignore').read()

        #Tokenize
    #    total_text = ucto(total_text)

        #Create and load lexicon
        print('  Create lexicon')

        if make_testfile:
            lexicon_filename = foldername+'/'+directory[:-1]+'.90.lex.txt' 
        else:
            lexicon_filename = foldername+'/'+directory[:-1]+'.lex.txt' 
        self.string_to_lexicon(total_text,lexicon_filename)
        lexicon = self.load_lexicon(lexicon_filename)

        #In simulation mode, cut away 10 percent for testing later
        print('  Make test file if needed')
        if make_testfile:
            testfilename = foldername+'/'+directory[:-1]+'.10.test.txt'
            training_filename = foldername+'/'+directory[:-1]+'.90.training.txt'

            words = total_text.split()
            boundary = round(len(words)*0.9)

            open(testfilename,'w').write(' '.join(words[boundary:]))
            total_text = ' '.join(words[:boundary])

        #In demo mode, just take all
        else:
            testfilename = ''
            training_filename = foldername+'/'+directory[:-1]+'.training.txt'

        #Attenuate the string with the training text
        print('  Attenuate string')
        total_text = self.attenuate_string_multicore(total_text,lexicon)

        #Make into ngrams, and save the file
        print('  Make ngrams')
        ngrams = self.make_ngrams(total_text)

        print('  Create file')
        training_file_content = '\n'.join(ngrams)
        open(training_filename,'w').write(training_file_content)

        #Return the filenames
        return training_filename, testfilename, lexicon

    def make_ngrams(self,text):
        """Transforms a string into a list of 4-grams, using multiple cores"""

        result = multiprocessing.Queue()

        #Starts the workers
        def worker(nr,string,result):

            if self.approach == 'w':
                if nr == 0:
                    ngrams = timbl.window_string(string,True)
                else:
                    ngrams = timbl.window_string(string)
            elif self.approach == 'l':
                if nr == 0:
                    ngrams = timbl.window_string_letters(string,True)
                else:
                    ngrams = timbl.window_string_letters(string)

            result.put((nr,ngrams))

        if self.approach == 'w':
            substrings = timbl.divide_iterable(text.split(),10,3)
        elif self.approach == 'l':
            substrings = timbl.divide_iterable(text,10,15)    

        for n,i in enumerate(substrings):
            t = multiprocessing.Process(target=worker,args=[n,i,result])
            t.start()

        #Wait until all results are in
        resultlist = []

        while len(resultlist) < 10:

            while not result.empty():
                resultlist.append(result.get())

            time.sleep(1)

        #Sort and merge the results
        resultlist = sorted(resultlist,key=lambda x:x[0])
        between_result = [x[1] for x in resultlist]    
        end_result = []
        for i in between_result:
            end_result += i

        return end_result

    def train_model(self,filename,mode):
        """Train a model on the basis of these ngrams"""

        command('timbl -f '+filename+' -I '+filename+'.IGTree +D +vdb -a1 -p 1000000',False)
        filename = filename.replace('.training.txt','').split('/')[-1];
        return Languagemodel(filename,self.approach,mode);

    def string_to_lexicon(self,string,outputfilename):
        """Creates a lexicon from a string"""

        #Counts words
        words = string.replace('\n','').split()
        counts = {}

        for i in words:
            try:
                counts[i] += 1
            except KeyError:
                counts[i] = 1

        #Sort words, most frequent first
        counts = sorted(list(counts.items()),key=lambda x: x[1],reverse=True)

        #Save results
        lines = ''

        for i in counts:
            lines += i[0] + ' ' +str(i[1]) + '\n'

        open(outputfilename,'w').write(lines)

    def load_lexicon(self,filename):
        """Returns a list of all words more frequent than threshold"""

        lexicon = open(filename,'r')
        frequent_words = {}

        for i in lexicon:
            word,frequency = i.split()
            frequency = int(frequency)

            if frequency > self.att_threshold:
                try:
                    frequent_words[len(word)].append(word)
                except KeyError:
                    frequent_words[len(word)] = [word]

        return frequent_words

    def attenuate_string_simple(self,string,lex):
        """Replaces infrequent words in string with #DUMMY, using one core"""

        words = string.split()
        result = ''

        for i in words:
            try:
                if i not in lex[len(i)]:
                    result += ' #DUMMY'
                else:
                    result += ' ' + i
            except KeyError:
                result += ' #DUMMY'

        return result.strip()

    def attenuate_string_multicore(self,string,lex):
        """Replaces infrequent words in string with #DUMMY, using multiple cores"""

        #Prepare input and output
        words = string.split()
        word_nr = len(words)
        result = multiprocessing.Queue()

        #The actual work
        def dummify(n,word):        
            try:
                if not word in lex[len(word)] and word not in ['_']:
                    return '#DUMMY'
                else:
                    return word

            except KeyError:
                return '#DUMMY'

        #Starts the workers
        def worker(nr,words,result):
            resultstring = ''
            wordtotal = len(words)

            for n,i in enumerate(words):
                
                resultstring += ' ' + dummify(n,i)

                #Report progress of the first worker
                if nr == 0 and n%100000 == 0:
                    print('  ',n / wordtotal)

            result.put((nr,resultstring))

        substrings = timbl.divide_iterable(words,10)
        
        for n,i in enumerate(substrings):
            t = multiprocessing.Process(target=worker,args=[n,i,result])
            t.start()

        #Wait until all results are in
        resultlist = []

        while len(resultlist) < 10:

            while not result.empty():
                resultlist.append(result.get())

            time.sleep(1)

        #Sort and merge the results
        resultlist = sorted(resultlist,key=lambda x:x[0])
        actual_result = [x[1] for x in resultlist]
            
        return ' '.join(actual_result).strip()

    def attenuate_training_file(self,filename,lexicon):
        """Replaces infrequent words in trainingfile with #DUMMY"""

        f = open(filename,'r')

        newlines = []
            
        for i in f:
            words = i.replace('\n','').split()
            result = ''
            
            for j in words[:-1]:
                if j not in lexicon and j not in ['_']:
                    result += ' #DUMMY'
                else:
                    result += ' '+j

            result += ' '+words[-1]
            newlines.append(result.strip())

        open(filename,'w').write('\n'.join(newlines))

class Module():

    def __init__(self,ss,name,model,kind):
        self.ss = ss
        self.name = name
        self.modelname = model
        self.kind = kind
        self.timblserver = ss.timblservers[self.modelname]

    def run(self,current_word,boundary,nr):

        pick = ''
        second_pick = ''
        third_pick = ''
        predictions = []

        full_word = ''
        second_guess = ''
        third_guess = ''

        if self.kind == 'igtree':
            pick, second_pick, third_pick, predictions = self.ss.read_prediction_file(self.modelname,nr,current_word,boundary)

        elif self.kind == 'lex':
            pick,second_pick = self.ss.read_frequency_file(self.modelname,current_word,boundary)

        elif self.kind == 'unique':
            pick = self.ss.only_one_word_possible(self.modelname,current_word,boundary)

        elif self.kind == 'rb':
            if boundary > 0:
                pick = self.ss.read_recency_buffer(recency_buffer,current_word,boundary)                

        return pick, second_pick, third_pick, predictions

    def send_to_your_server(self,lcontext,nr):

        self.timblserver.send(lcontext)
        distr = ''

        while distr == '' or 'DISTRIBUTION' not in distr or distr[-1] != '\n':
            try:
                distr += self.timblserver.receive()
            except UnicodeError:
                distr = 'DISTRIBUTION { de 0.999 }\n'
                print('  Skipped one')

        final_distr = '[ word ]' + distr.split('DISTRIBUTION')[1]
        open('predictions/lcontext'+nr+'.'+self.modelname+'.IGTree.gr.out','w').write(final_distr)      

class Languagemodel():

    def __init__(self,name,approach,mode):

        self.approach = approach
        self.mode = mode
        self.name_raw = name

        if self.mode == 's':
            self.name = self.name_raw + '.90'
        else:
            self.name = self.name_raw

        if self.approach == 'w':
            self.folder = 'wordmodels'
        elif self.approach == 'l':
            self.folder = 'lettermodels'

        self.filename = self.name + '.training.txt.IGTree'
        self.location = self.folder + '/' + self.filename

def get_free_port():
    
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind(('',0))
    port = s.getsockname()[1]
    s.close()

    return int(port)

#TODO
# Basisinstellingen voor het language model
# Lexicon ook integreren als property
# TiMBL-object verwijderen? Server verwijderen
# Window_string verplaatsen: kun je nog wel modellen maken?

# Uitzoeken: hoe vaak komt het voor dat woorden gelijke confidence hebben?
# Server modus
# Mogelijk: werkt het beter als je na lang doorgaan stopt met suggereren?
# Lettermodus: gaat er ergens iets fout?
# Haakje sluiten in simulatiemodus
# Backspace: fout als je over de kleurgrenzen heen backspacet gaan de kleuren raar doen
