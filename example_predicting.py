import soothsayer

ss = soothsayer.Soothsayer();

#Load the language model
model = 'wordmodels/allmail';
ss.start_servers(model,True);

#Load the lexicon
lex = ss.load_lexicon('wordmodels/allmail.lex.txt');

#Ask for prediction after every letter
teststring = 'Dit is een zin om te testen';

for n,i in enumerate(teststring):
    pred = ss.do_prediction(teststring[:n],model,lex,'');
    print(pred['full_word'],pred['second_guess']);






##OUTPUT:
##  Using running server
##  Using running server
##_ Hoi
##Dear Dag
##Die Dit
##Dit Ditmaal
##zal is
##is in
##is isotoop
##wat de
##een eigenlijk
##een eenvoudig
##een eenvoudig
##idee overzicht
##zeer zogenaamde
##zin zichzelf
##zin zin
##als van
##op of
##om omdat
##het ze
##te the
##te tegen
##kijken horen
##testen the
##testen tegen
##testen testen
##testen testen
##testen
