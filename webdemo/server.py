import sys
sys.stdout = sys.stderr

import atexit
import threading
import cherrypy
import urllib2
import traceback
import os
import subprocess

#Paths
maindir = '/scratch2/www/soothsayer'

#CherryPy+WSGI related stuff
cherrypy.config.update({'environment': 'embedded'});
#cherrypy.log.error_file = maindir+'/cherry_errors/cherry_error.log'

test_tweeters = ['4rch1t3ct', 'corriebult', 'jboekelman', 'megasupernieuws', 'sredlums',
            'aafkebrons', 'deesje34', 'jdpoohbear', 'micheldebruijn', 'steephsel',
            'aardengelpiet', 'deheldin', 'jennekepenneke', 'miekeinc', 'tasvolverhalen',
            'agatha_make_up', 'dennismons', 'jessiesissammy', 'mitzyoss', 
            'aldith_hunkar', 'devrouwthuis', 'jettyvanrooy', '_mrs', 'texas12345',
            'eetschrijver', 'jndkgrf', 'mrsmartine', 'the_ed', 'amadeusivan', 'elmavonk',
            'johnschop', 'musjes', 'tibetanpaddy', 'a_mieke', 'erwblo', 'josvrbk',
            'nabilfeki', 'tien020', 'analons', 'esther_305', 'karinwinters',
            'titchener', 'ewdevlieger', 'klapster', 'tourdejose',
            'anniebbarks', 'fluist3r', 'knotsbots', 'tponl', 'archatoz', 'fred3012',
            'kos_', 'ongerijmd', 'tvgeneuzel', 'artbysophia', 'godpipo', 'k_ruiter',
            'paulzornig', 'umarebru', 'baspaternotte', 'goedemorgenman', 'leolewin',
            'peterstafleu', 'vic23', 'bas_taart', 'gradjuh', 'lexcje', 'pienbetuwe',
            'victorward', 'beanobrien13', 'harveycusick', 'liekelamb', 'pinaatje',
            'walterhoekstra', 'henkkanning', 'lobdozer', 'politicus1',
            'whippetpickle', 'boswachterfrans', 'hetspijtme', 'puberdochters', 'wup5',
            'brechtjedeleij', 'house_fd', 'mariannecramer', 'rebelsnotes', 'w_veldhorst',
            'casvries', 'humfthecocker', 'marjasandersnl', 'rider_ot_storm',
            'zijhiernaast', 'chrisklomp', 'ikke_mij_deze', 'marktwain2', 'rjvanhouten',
            'contentgirl', 'jasmijn02', 'maupienco', 'roosvanvugt'];

def feed_to_display(feed):

    if '.lex.txt' not in feed:
        return False;

    for i in ['community','fakecomm','nl.lex.txt','nlsave','allmail','xs','latin',
              'andrekuipers','trashfashion','testinput'] + test_tweeters:
        if i in feed:
            return False;

    return True;

def command(c):

    p = subprocess.Popen(c.split(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT);
    return p.stdout.read();

#How the server should respond
class webdemo(object):

    def index(self,user=''):
        """"Shows the mainpage""";

#        return open(maindir+'/webdemo/errorpage.htm').read();

        template = open(maindir+'/webdemo/demopage.htm').read();
        standard_form = '<div id="premade_models"><form><select id="pickvalue"><option value="allmail">Verzonden emails van Wessel</option><option value="andrekuipers">Weblog Andre Kuipers</option><option value="trashfashion">Weblog Trashfashion (Sabine Oudt)</option><option value="borsato">Tweets van Marco Borsato</option><option value="youpvanthek">Tweets van Youp van \'t Hek</option></select></form></div><div id="own_model"><a href="get_models">OF gebruik een taalmodel gebaseerd op je eigen tweets</a></div>';

        if user == '':
            form = standard_form;
        else:
            form = '<div id="pickvalue">Taalmodel: '+str(user)+' (<a href="get_models">Kies een ander</a>)</div>';

        return template.replace('%form%',form);
    index.exposed = True

    def index2(self,user=''):
        """"Shows the mainpage""";

        template = open(maindir+'/webdemo/demopage.htm').read();
        standard_form = '<div id="premade_models"><form><select id="pickvalue"><option value="allmail">Verzonden emails van Wessel</option><option value="andrekuipers">Weblog Andre Kuipers</option><option value="trashfashion">Weblog Trashfashion (Sabine Oudt)</option><option value="borsato">Tweets van Marco Borsato</option><option value="youpvanthek">Tweets van Youp van \'t Hek</option></select></form></div><div id="own_model"><a href="get_models">OF gebruik een taalmodel gebaseerd op je eigen tweets</a></div>';

        if user == '':
            form = standard_form;
        else:
            form = '<div id="pickvalue">Taalmodel: '+str(user)+' (<a href="get_models">Kies een ander</a>)</div>';

        return template.replace('%form%',form);
    index2.exposed = True


    def predict(self,text,model,show_source=0,n_predictions=1):
        """Asks Soothsayer for a prediction""";

        try:
            return urllib2.urlopen('http://0.0.0.0:4000/predict?text='+text+'&model='+model+'&show_source='+str(show_source)+'&n_predictions='+str(n_predictions));
        except:
            return traceback.format_exc(); 
    predict.exposed = True



    def load_model(self,model):
        """Loads a language model in memory""";

        #return urllib2.urlopen('http://0.0.0.0:4000/load_model?model='+model)
        urllib2.urlopen('http://0.0.0.0:4000/load_model?model='+model)
        return '<script type="text/javascript">window.location.replace("index?user='+model+'");</script>';

    load_model.exposed = True



    def get_models(self):
        """Displays all language models made earlier""";

        #Create the page
        template = open(maindir+'/webdemo/template.htm').read()
        body = '<p>Kies hier je Twitternaam (of die van iemand anders). Staat je naam niet in de lijst? Dan moet jouw taalmodel nog aangemaakt worden. <a href="create_model">Klik hier</a> om dat te doen.</p><ul>';        

        #Get which models are available
        try:
            files = os.listdir(maindir+'/repo/soothsayer/wordmodels');
            feeds = [];
        except:
            return traceback.format_exc();
        
        for i in files:
            if feed_to_display(i):
                feeds.append(i.replace('.lex.txt','').replace('.90','').replace('@',''));

        #Sort and remove duplicates
        feeds = list(set(feeds));
        feeds.sort();

        #Display them all
        for i in feeds:
            body += '<li><a href="load_model?model='+i+'">'+i+'</a></li>';            

        body+= '</ul>';

        return template.replace('%BODY%',body);
    get_models.exposed = True;



    def create_model(self):
        """Shows the page where the user can create a new language model""";

        template = open(maindir+'/webdemo/template.htm').read();
        body = '<script type="text/javascript">'+open(maindir+'/webdemo/create_model.js').read()+'</script>';
        body += '<p>Voor welke Twittergebruiker wil je een taalmodel maken?</p>'+\
                '<form><input class="user" type="text"/><br/><br/><input class="button" '+\
                'type="button" value="Create"></form><p class="logtext"></p><img src="http://www.lenovodreamtodo.com/img/fbapps/iremember/loadingAnimation.gif">';
        return template.replace('%BODY%',body);
    create_model.exposed = True;



    def create_model_procedure(self,user):
        """Runs all scripts necessary for creating a language model""";

        user = str(user);

        #Create log file
        logfilename = maindir+'/logs/create_model_'+user+'.txt';
        log = open(logfilename,'w',0);

        #Import the tweets        
        log.write('<p>Tweets van '+user+' worden geimporteerd</p>');

        try:
            output = command('python '+maindir+'/webdemo/feed_to_input.py '+user);
            #log.write(output);

            command('chmod a+w+r '+maindir+'/repo/soothsayer/input/'+user);
            command('chmod a+w+r '+maindir+'/repo/soothsayer/input/'+user+'/'+user);

        except:
            import traceback;
            return traceback.format_exc();

        log.write('<p>Tweets geimporteerd</p>');

        #Create language model
        log.write('<p>Taalmodel wordt aangemaakt</p>');
              
        try:
            output = command('python3 '+maindir+'/repo/soothsayer/input_to_model.py '+user);
            #log.write(output);
        except:
            import traceback;
            return traceback.format_exc();

        log.write('<p>Taalmodel aangemaakt</p>');

        #Create file to save the tweets
        try:
            open(maindir+'/repo/soothsayer/predictions/lcontext.'+user+'.IGTree.gr.out','w').write('... ] { ...');
        except:
            import traceback;
            return traceback.format_exc();

        log.write('<p><a href="load_model?model='+user+'">Klik hier</a> om je taalmodel te testen</p>');

        log = open(logfilename);
        return log.read();   
    create_model_procedure.exposed = True;


    def log_file(self,user):
        """Returns the current logfile for the model creation of a user""";
        return open(maindir+'/logs/create_model_'+user+'.txt').read();
    log_file.exposed = True;

      
soothsayers = {}
lexicons = {};
application = cherrypy.Application(webdemo(), script_name=None, config=None)
