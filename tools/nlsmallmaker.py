import os
import random

for i in range(3000):
    if i%100 == 0:
        print(i);

    pick = random.choice(os.listdir('nl'));
    content = open('nl/'+pick,'r').read();
    open('nlsmall/'+pick,'w').write(content);
