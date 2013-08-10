import soothsayer

ss = soothsayer.Soothsayer();

#Soothsayer takes a directory of plaintext files as input
training_file, testfile, lexicon = ss.prepare_training_data('testinput/');
model = ss.train_model(training_file, mode='w');

print(model.name);




## OUTPUT
##  Grab all files
##    0.0
##  Create lexicon
##  Make test file if needed
##  Attenuate string
##   0.0
##  Make ngrams
##  Create file
## wordmodels/testinput
