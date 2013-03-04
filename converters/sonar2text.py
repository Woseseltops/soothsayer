import os
import xml.dom.minidom as xml
import cgi

def get_content(node):

    for j in node.childNodes:
        if j.nodeType == j.TEXT_NODE:
            return cgi.escape(j.data).encode('ascii','xmlcharrefreplace').decode();    

#fol = '/vol/bigdata/corpora/SoNaR500/SONAR500/DATA/WR-P-E-K_blogs/';
#fol = '/vol/bigdata/corpora/SoNaR500/SONAR500/DATA/WR-P-E-J_wikipedia/';
fol = '/vol/bigdata/corpora/SoNaR500/SONAR500/DATA/WR-P-P-H_periodicals_magazines/';
names = os.listdir(fol);

for i in names[500:1000]:
    print(i);
    if not 'cmdi' in i:
        string = open(fol+'/'+i,'r').read();
        text = xml.parseString(string).getElementsByTagName('t');
        total = '';

        for j in text:
            try:
                total += ' '+ get_content(j);
            except:
                pass;

        open('nl/'+i[:-4],'w').write(total);

