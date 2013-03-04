import os;
import email.parser as parser;

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

                content = ' '.join(new_content).replace('= ','').replace(' ----- Oorspronkelijk bericht -----','').replace('----- Doorgestuurd bericht -----','').replace('=C3=A9','e');
                return(content);    

    return '';

inputdir = '/scratch/wstoop/mail/Sent!5/';

files = os.listdir(inputdir);

for i in files:
    if i[-4:] == '.eml':

        mail = open(inputdir+i,'r').read();
        print(get_email_content(mail));
