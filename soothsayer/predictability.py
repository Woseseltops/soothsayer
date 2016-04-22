from urllib.request import urlopen
import soothsayer

def string_position_to_word_position(string,string_position):
    """The 15th character in this sentence is the 6th character in its word"""

    found_space_or_sentence_onset = False
    current_position = string_position

    while not found_space_or_sentence_onset:
        
        if current_position < 0 or string[current_position] in ' _':
            found_space_or_sentence_onset = True

        else:
            current_position -=1

    return string_position - current_position -1

def get_predictability_for_sentence(sentence,base_location='',lexicon_location='wordmodels/allmail.lex.txt',verbose=False):

    ss = soothsayer.Soothsayer()
    ss.base_location = base_location

    #Load the language models
    pers_model = soothsayer.Languagemodel('allmail','w','d')
    bg_model = soothsayer.Languagemodel('nlsave','w','d')

    try:
        ss.start_servers([pers_model,bg_model],True)
    except: #psutil error
        return 0

    #Load the lexicon
    lex = ss.load_lexicon(lexicon_location)

    #Set the module order
    ss.setup_basic_modules(pers_model)    

    last_prediction = ''
    sentence_so_far = ''
    number_of_correctly_predicted_letters = 0

    for n, letter in enumerate(sentence):    
    
        if n%1000 == 0:
            print(str(n)+'/'+str(len(sentence)))

        position_in_word = string_position_to_word_position(sentence,n)

        if letter not in ' _,.!?':
            prediction = ss.do_prediction(sentence_so_far,lex,'')['full_word']

            try:
                predicted_letter = prediction[position_in_word]        
            except IndexError:
                predicted_letter = ''

            if letter == predicted_letter:
                number_of_correctly_predicted_letters += 1

            if verbose:
                print(letter,predicted_letter,prediction)

        elif letter in ',.!?':
            number_of_correctly_predicted_letters += 1

        sentence_so_far += letter

    return number_of_correctly_predicted_letters/len(sentence)

def get_predictability_for_sentence_from_server(sentence,webserver_url,verbose=False):
    
    URL_EXTENSION_FOR_PREDICTION = 'predict?model=allmail&text='
    last_prediction = ''
    sentence_so_far = ''
    number_of_correctly_predicted_letters = 0

    for n, letter in enumerate(sentence):    
    
        letter = letter.replace(' ','_')
        position_in_word = string_position_to_word_position(sentence,n)

        if letter not in ' _,.!?':
            prediction = urlopen(webserver_url+URL_EXTENSION_FOR_PREDICTION+sentence_so_far).read().decode().split(',')[0]

            try:
                predicted_letter = prediction[position_in_word]        
            except IndexError:
                predicted_letter = ''

            if letter == predicted_letter:
                number_of_correctly_predicted_letters += 1
        elif letter in ',.!?':
            number_of_correctly_predicted_letters += 1

        if verbose:
            print(letter,predicted_letter,prediction)

        sentence_so_far += letter

    return number_of_correctly_predicted_letters/len(sentence)

if __name__ == '__main__':

    USE_SERVER = False
    WEBSERVER_URL = 'http://soothsayer.cls.ru.nl/'

    if USE_SERVER:
        p = get_predictability_for_sentence_from_server('Top 10 leukste functietitels voor vrijwilligerswerk',WEBSERVER_URL,verbose=True)
    else:
        p = get_predictability_for_sentence(100*'Dit is een testzin ',verbose=True)

    print(p)
