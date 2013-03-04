import multiprocessing

def hard_work():

    x = 1;

    for i in range(100000000):

       x = i * i * x;

for i in range(10):
    t = multiprocessing.Process(target = hard_work);
    t.start();
