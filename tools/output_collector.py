import os

loc = '/vol/bigdata/users/wstoop/soothsayer/output/';
files = os.listdir(loc);

for i in files:
    name = i.split('.')[-1];
    
    f = open(loc+i);
    cks = f.readline().split()[-1];
    skks = f.readline().split()[-1]; 

    print(name,cks,skks);
