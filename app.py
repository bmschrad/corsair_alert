import time
import json
import pickle
import logging
from cuepy import CorsairSDK
from datetime import datetime, timedelta
from itertools import cycle

### Setup ###

logging.basicConfig(level=logging.DEBUG)

#Led locations
LED_LOGO = 148
LED_BOTTOM = 149
LED_SCROLL = 150

# Timer Settings (all in seconds)
LED_DELAY = 1
UPDATE_DELAY = 20
hb_threshold = 7 # Time in minutes
iso_format = '%Y-%m-%dT%H:%M:%S' # Used to parse hb back into object

#Corsair SDK library location
sdk = CorsairSDK("C:\\CUESDK.x64_2013.dll")
### End Setup ###

### Warning Colors ###
ALERT_HB = [255,0,0]
ALERT_TMHP = [255,255,0]
ALERT_MDS = [255,0,0]
ALERT_PBJ = [255,255,0]
ALERT_REPORTS = [0,255,0]
ALERT_CFS = [0,0,255]
### End Warning Colors ###

# Init sequence
def init_device():
   if(sdk.device_count() >= 1):
       print('Found the following device:')
       for k, v in sdk.device_info(0).items():
           print('\t',k,v)
       return sdk.device(0)
   else:
       print('No device found')


# Reset all leds to off
def led_reset(device):
    device.set_led(LED_LOGO,[0,0,0])
    device.set_led(LED_BOTTOM,[0,0,0])
    device.set_led(LED_SCROLL,[0,0,0])


# Process lighting queue
def process_leds(device, queus):

    #Find out which queus is larger and use that for the driver
    if(len(queus['scroll']) > len(queus['logo'])):
       i = cycle(queus['logo'])
       for q in queus['scroll']:
           print('SCROLL LOOP {}'.format(q))
           device.set_led(LED_SCROLL,q)
           device.set_led(LED_LOGO, next(i))
           time.sleep(LED_DELAY)
    else:
       i = cycle(queus['scroll'])
       for q in queus['logo']:
           print('LOGO LOOP {}'.format(q))
           device.set_led(LED_LOGO,q)
           device.set_led(LED_SCROLL, next(i))
           time.sleep(LED_DELAY)


# HB processing logic
def bad_hb(heartbeat, th):
    # Remove the microseconds to make it easier on ourselves
    heartbeat = heartbeat.split('.')[0]
    hb = datetime.strptime(heartbeat, iso_format)
    deadline = datetime.utcnow() - timedelta(minutes=th)
    return deadline > hb


# Message Processing 
def process_msg(message):

    led_queue = {}
    led_queue['scroll'] = []
    led_queue['logo'] = []

    msg = json.loads(message)

    # Make sure heartbeat isn't behind
    if bad_hb(msg['hb'], hb_threshold): led_queue['logo'].append(ALERT_HB)
    if msg['tmhp_up'] == False: led_queue['logo'].append(ALERT_TMHP)

    # Check for any alerts
    for a in msg['alerts']:
        if a == 'mds_batches': led_queue['scroll'].append(ALERT_MDS)
        elif a == 'pbj_batches': led_queue['scroll'].append(ALERT_PBJ)
        elif a == 'overdue_reports': led_queue['scroll'].append(ALERT_REPORTS)
        elif a == 'cfs_forms': led_queue['scroll'].append(ALERT_CFS)

    # If any of the queues are empty set them to the ok status
    if(len(led_queue['scroll']) == 0): led_queue['scroll'].append([0,0,0])
    if(len(led_queue['logo']) == 0): led_queue['logo'].append([0,0,10])
    
    return led_queue

# General run sequence
def run():

    logging.info('Corsair Alert Started')

    # Initialize mouse
    device = init_device()
    msg = {}

    # Set last run within threshold so it runs first
    last_run = datetime.now() - (timedelta(seconds=UPDATE_DELAY + 1))
    
    while(1):

	# Make sure we only update within the alloted time
        if datetime.now() > last_run + timedelta(seconds=UPDATE_DELAY):
            #Load new pickle file and process message
            logging.debug('Updating Pickle')
            with open('ops_status.pickle', 'rb') as f:
                msg = pickle.load(f)
                #logging.debug('New Pickle:\n{}'.format(msg))

            msg# Increment last run
            last_run = datetime.now()
        
        # Process message and cycle through queue
        q = process_msg(json.dumps(msg))
        process_leds(device, q)



if __name__ == "__main__":
   run()
