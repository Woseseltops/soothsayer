"""This script queries the server to see what extent a sentence is predictable by the language model run by that server"""

from urllib.request import urlopen

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

def get_predictability_for_sentence(sentence,webserver_url,verbose=False):
	
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
                predicted_letter = prediction[position_in_word];        
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

    WEBSERVER_URL = 'http://soothsayer.cls.ru.nl/'

    p = get_predictability_for_sentence('Top 10 leukste functietitels voor vrijwilligerswerk',WEBSERVER_URL,verbose=True)
    print(p)
