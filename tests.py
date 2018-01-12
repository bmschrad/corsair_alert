from app import *
from alert_msg_tests import *
import time
import logging

WAIT_TIME = 3 


def run_tests():

    # Initialize device and drivers
    device = init_device()

    # Reset to normal lights
    led_reset(device)

    # Loop through test messages
    logging.info('---------------\n\n')
    logging.info('Running Test:\n')
    for m in msgs:
        logging.info('-- {0}\n{1}\n'.format(m, json.dumps(msgs[m], indent=2, sort_keys=True)))
        q = process_msg(msgs[m])
        process_leds(device, q)
        process_leds(device, q)
        time.sleep(WAIT_TIME)


if __name__ == '__main__':
    run_tests()
