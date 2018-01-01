from app import *
from alert_msg_tests import *
import time

WAIT_TIME = 5 


def run_tests():

    # Initialize device and drivers
    device = init_device()

    # Reset to normal lights
    led_reset(device)

    # Loop through test messages
    for m in msgs:
        print('Running Message: {}'.format(m))
        q = process_msg(msgs[m])
        process_leds(device, q)
        process_leds(device, q)
        time.sleep(WAIT_TIME)


if __name__ == '__main__':
    run_tests()
