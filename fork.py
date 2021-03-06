from common import *
from os.path import join, dirname
import splunk_deployment
import logging
import shutil
import threading
import time
from sys import stdout

logger = logging.getLogger(__name__)
splunk_deployment = splunk_deployment.SplunkDeployment()

def fork(args):
    splunk = splunk_deployment.get_splunk(args['splunk'])
    
    # check if already forked
    if splunk_deployment.contains(splunk.get_name()+'-forked'):
        print splunk.get_name() + ' is already forked'
        exit()

    if splunk.is_running():
        splunk.stop()

    # copy files
    try:
        t = threading.Thread(target = lambda: shutil.copytree(splunk.get_path(), 
            join(dirname(splunk.get_path()), splunk.get_name()+'-forked')))

        t.start()
        stdout.write('forking')
        
        while t.is_alive():
            stdout.write ('.')
            stdout.flush()
            time.sleep(1)

        stdout.write('\n')


        splunk_deployment.refresh()

    except Exception as err:
        print 'failed to fork {splunk}'.format(splunk=splunk.get_name())
        logger.error(err)
        exit()

    except KeyboardInterrupt:
        print '\ncan\'t interrupt, please wait for forking to complete'
        t.join()
        exit()

    # change port
    splunk_forked = splunk_deployment.get_splunk(splunk.get_name()+'-forked')
    splunk_forked.run_command(['set','web-port','8010'])
    splunk_forked.run_command(['set','splunkd-port','8099'])
    splunk_forked.run_command(['set','kvstore-port','8181'])
    splunk_forked.run_command(['set','appserver-ports','8075'])

    print 'web port:\t8010\nmgmt port:\t8099\nkvstore port:\t8181\nappserver port:\t8075'

    if args['start']:
        splunk.start()
        splunk_forked.start()


