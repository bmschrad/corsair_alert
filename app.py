import time
import json
from cuepy import CorsairSDK
from itertools import cycle

### Setup ###

#Led locations
LED_LOGO = 148
LED_BOTTOM = 149
LED_SCROLL = 150

# Timer Settings (all in seconds)
LED_DELAY = 1

#Corsair SDK library location
sdk = CorsairSDK("C:\\CUESDK.x64_2013.dll")
### End Setup ###

### Warning Colors ###
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


# Message Processing 
def process_msg(message):

    led_queue = {}
    led_queue['scroll'] = []
    led_queue['logo'] = []

    msg = json.loads(message)
    print('Processing Message: \n{}'.format(msg))

    # Make sure heartbeat isn't behind
    # TODO: DO THIS WHEN THE DATE CONVERSION IS FIGUED OUT
    #hb = datetime.utcnow(msg['heartbeat'])

    if(msg['tmhp_up'] == False): led_queue['logo'].append(ALERT_TMHP)

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
    init_device()
    time.sleep(100)

if __name__ == "__main__":
   run()
