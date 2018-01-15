import config
import requests
import time
import json
import pickle
import logging
from cuepy import CorsairSDK
from datetime import datetime, timedelta
from itertools import cycle

### Setup ###
logging.basicConfig(level=config.log_level, format=config.log_format)

#Led locations
LED_LOGO = 148
LED_BOTTOM = 149
LED_SCROLL = 150

# Headstand leds
# Start from the back
HS_BASE = \
    [199, 192, 193, \
     194, 195, 196, \
     197, 198]
HS_LOGO = 191

iso_format = '%Y-%m-%dT%H:%M:%S' # Used to parse hb back into object

#Corsair SDK library location
sdk = CorsairSDK(config.sdk_path)
PICKLE_PATH = ''
### End Setup ###

### Warning Colors ###
ALERT_HB = [255,0,0]
ALERT_TMHP = [255,255,0]
ALERT_MDS = [255,0,0]
ALERT_PBJ = [255,255,0]
ALERT_REPORTS = [0,255,0]
ALERT_CFS = [0,0,255]
ALERT_CFS_LTCMI = [0,0,128]
### End Warning Colors ###

### Default Colors ###
ALERT_LOGO_DEFAULT = [0, 0, 0]
ALERT_BASE_DEFAULT = [0, 255, 0]
### End Default Colors ###

# Init sequence
def init_device():
   if(sdk.device_count() >= 1):
       logging.info('Found the following device:')
       for k, v in sdk.device_info(0).items():
           logging.info('\t{} {}'.format(k,v))
       return sdk.device(0)
   else:
       logging.error('No device found')


# Reset all leds to off
def led_reset(device):
    process_base_leds(device,[0,0,0])


# Change all Headset base colors
def process_base_leds(device, color):
    
    for i in HS_BASE:
        #logging.debug('Processing base LED: {} to color {}'.format(i, color))
        device.set_led(i, color)


# Process lighting queue
def process_leds(device, queus):

    #Find out which queus is larger and use that for the driver
    if(len(queus['base']) > len(queus['logo'])):
       i = cycle(queus['logo'])
       for q in queus['base']:
           #logging.debug('BASE LOOP {}'.format(q))
           process_base_leds(device, q)
           device.set_led(HS_LOGO, next(i))
           time.sleep(config.LED_DELAY)
    else:
       i = cycle(queus['base'])
       for q in queus['logo']:
           #logging.debug('LOGO LOOP {}'.format(q))
           device.set_led(HS_LOGO,q)
           process_base_leds(device, next(i))
           time.sleep(config.LED_DELAY)


# HB processing logic
def bad_hb(heartbeat, th):
    # Remove the microseconds to make it easier on ourselves
    heartbeat = heartbeat.split('.')[0]
    hb = datetime.strptime(heartbeat, iso_format)
    deadline = datetime.now() - timedelta(minutes=th)
    return deadline > hb


# Message Processing 
def process_msg(message):

    led_queue = {}
    led_queue['base'] = []
    led_queue['logo'] = []

    msg = json.loads(message)

    # Make sure heartbeat isn't behind
    if bad_hb(msg['hb'], config.hb_threshold): led_queue['base'].append(ALERT_HB)
    if msg['tmhp_up'] == False: led_queue['base'].append(ALERT_TMHP)

    # Check for any alerts
    for a in msg['alerts']:
        if a == 'mds_batches': led_queue['logo'].append(ALERT_MDS)
        elif a == 'pbj_batches': led_queue['logo'].append(ALERT_PBJ)
        elif a == 'overdue_reports': led_queue['logo'].append(ALERT_REPORTS)
        elif a == 'cfs_forms': 
            # See if any of the forms are LTCMI
            has_ltcmi = False
            for i in msg['alerts'][a]:
                if i['form_type'] == 'LTCMI 3': has_ltcmi = True
            if has_ltcmi: led_queue['logo'].append(ALERT_CFS_LTCMI)
            led_queue['logo'].append(ALERT_CFS)

    # If any of the queues are empty set them to the ok status
    if(len(led_queue['base']) == 0): led_queue['base'].append(ALERT_BASE_DEFAULT)
    if(len(led_queue['logo']) == 0): led_queue['logo'].append(ALERT_LOGO_DEFAULT)
    
    return led_queue


# Get Pickle File message
def process_pickle():
    
    #Load new pickle file
    with open(PICKLE_PATH, 'rb') as f:
        msg = pickle.load(f)

    logging.info('Updating Pickle')
    return json.dumps(msg)


# Get Ops Api message
def process_ops_api():
    
    #Load new ops api status
    uri = '{}/status/health'.format(config.ops_api_uri)
    logging.debug('Requesting status from: {}'.format(uri))
    
    res = requests.get(url=uri, verify=config.api_crt)
    if res.ok:
        logging.info('Updated from API')
        return res.text
    else:
        logging.error('API Returned: {}, {}'.format(res.status_code, res.text))
        return ''


# General run sequence
def run(get_msg_proc):

    # Initialize mouse
    device = init_device()
    msg = {}

    # Set last run within threshold so it runs first
    last_run = datetime.now() - (timedelta(seconds=config.UPDATE_DELAY + 1))
    
    while(1):

	# Make sure we only update within the alloted time
        if datetime.now() > last_run + timedelta(seconds=config.UPDATE_DELAY):

            # Time to get the new message
            new_msg = get_msg_proc()

            # Make sure we get a message back then process
            if new_msg != '':
                logging.debug('{}'.format(json.dumps(json.loads(new_msg), indent=2, sort_keys=True)))
                msg = new_msg
                # Increment last run
                last_run = datetime.now()

        q = process_msg(msg)
        process_leds(device, q)
        


def get_parser():
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    parser = ArgumentParser(description=__doc__, \
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-f", "--file", \
                        dest="filename", \
                        help="write output to pickle file", \
                        metavar="FILE")
    return parser


if __name__ == "__main__":

    logging.info('Corsair Alert Started')

    # See what we need to set our output to
    args = get_parser().parse_args()
    if args.filename is not None:
        PICKLE_PATH = args.filename
        logging.info('Pickle Path: {}'.format(PICKLE_PATH))
        get_msg_proc = process_pickle
    else:
        if config.ops_api_uri is not None:
            logging.info('Ops API URI: {}'.format(config.ops_api_uri))
            get_msg_proc = process_ops_api
        else:
            logging.error("PICKLE_PATH or OPS_API_URI enviroment variable not set")
            exit()
    
    run(get_msg_proc)
