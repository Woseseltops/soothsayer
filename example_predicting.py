import soothsayer

ss = soothsayer.Soothsayer();

#Load the language models
pers_model = soothsayer.Languagemodel('testinput','w','d');
ss.start_servers([pers_model],True);

#Load the lexicon
lex = ss.load_lexicon('wordmodels/testinput.lex.txt');

#Set the module order
ss.modules = [soothsayer.Module(ss,'context-sensitive module',pers_model.name,'igtree'),
              soothsayer.Module(ss,'context-insensitive module',pers_model.name,'lex'),]

#Ask for prediction after every letter
teststring = 'Dit is een zin om te testen';

for n,i in enumerate(teststring):
    pred = ss.do_prediction(teststring[:n],lex,'');
    print(teststring[:n], pred['full_word'],'(',pred['second_guess'],')');






##OUTPUT:
## Dit ( is )
##D Dit (  )
##Di Dit (  )
##Dit Dit (  )
##Dit  is ( ook )
##Dit i is (  )
##Dit is is (  )
##Dit is  een (  )
##Dit is e een (  )
##Dit is ee een (  )
##Dit is een een (  )
##Dit is een   (  )
##Dit is een z  (  )
##Dit is een zi  (  )
##Dit is een zin  (  )
##Dit is een zin  Dit ( is )
##Dit is een zin o ook (  )
##Dit is een zin om  (  )
##Dit is een zin om  Dit ( is )
##Dit is een zin om t testzin.Dit (  )
##Dit is een zin om te testzin.Dit (  )
##Dit is een zin om te  Dit ( is )
##Dit is een zin om te t testzin.Dit (  )
##Dit is een zin om te te testzin.Dit (  )
##Dit is een zin om te tes testzin.Dit (  )
##Dit is een zin om te test testzin.Dit (  )
##Dit is een zin om te teste  (  )
