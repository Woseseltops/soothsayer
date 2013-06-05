inp = open('input/borsato/borsato');
outp = 'input/borsato/borsato_content';

open(outp,'w');
outp = open(outp,'a');

for i in inp:
    content = i.split('||')[-1];
    outp.write(content);
