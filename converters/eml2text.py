import os;
import email.parser as parser;
import re;

def remove_weird_chars(string):

    return re.sub(r'=[0-9][A-Z]','',string);

def get_email_content(mail):
    """Extracts the actual message from an email""";

    msg = parser.Parser().parsestr(mail);
    for part in msg.walk():
        if part.get_content_type() == 'text/plain':
            text = part.get_payload();

            if len(text) < 3000:
                raw_content = part.get_payload().split('\n');
                new_content = [];

                for i in raw_content:
                    if len(i) > 0 and i[0] not in ['-','>']:
                        new_content.append(i);

                content = remove_weird_chars(' '.join(new_content).replace(' ----- Oorspronkelijk bericht -----','').replace('----- Doorgestuurd bericht -----','')).replace('=','');
                return(content);    

    return '';


inputdir = '/scratch/wstoop/mail/Sent!7/';

files = os.listdir(inputdir);

c = 3464;

for i in files:
    if i[-4:] == '.eml':

        mail = open(inputdir+i,'r').read();
        open('/scratch/wstoop/mail/allmail/'+str(c),'w').write(get_email_content(mail));
	c += 1;

print(c);
