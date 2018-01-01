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
    device.set_led(LED_LOGO,[0,0,10])
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
def process_msg(device, msg):
    req = json.loads(msg)
    print(msg)
    print('Processing Message: \n{}'.format(req))
    #print('Processing Message: \n{}'.format(pprint.pprint(req)))

    # Reset the mouse leds to default
    led_reset(device)

    # Make sure heartbeat isn't behind

# General run sequence
def run():
    init_device()
    time.sleep(100)

if __name__ == "__main__":
   run()
