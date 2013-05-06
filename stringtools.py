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

