import sys
import soothsayer

ss = soothsayer.Soothsayer(att_threshold=0);

#Soothsayer takes a directory of plaintext files as input
training_file, testfile, lexicon = ss.prepare_training_data(sys.argv[1]+'/');
model = ss.train_model(training_file,'d');
