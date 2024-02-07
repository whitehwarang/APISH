import os


##### General Configuration #####
INDI_OBJ_PATH = 'C:\\SHINHAN-i\\indi\\giexpertstarter.exe'

#################################

##### Logger Configuration #####
LOG_DIR = 'APISH2\\Log\\'
################################
if not os.path.isdir(LOG_DIR):
    os.makedirs(LOG_DIR)

