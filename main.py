#! /usr/bin/env python3
# -*- coding : utf-8 -*-

import config as cfg
import requests
import os
import RPi.GPIO as GPIO
from leMET import get_next_buses
from LEDController import LEDController
from time import sleep, time


OFF_HOLD_TIME = 3 # Holding the button for three seconds will turn off the Raspberry Pi

# GPIO pins
SEGMENT_PINS = (26, 6, 13, 20, 19, 16, 12)
DIGIT_PINS = ((5, 1), (0, 7))
TEL_PINS = (8, 11)
BUTTON_PIN = 25


# Setting up LEDs and button
LED_CONTROLLER = LEDController(SEGMENT_PINS, DIGIT_PINS, TEL_PINS)

GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
LED_CONTROLLER.all_on()
sleep(1)


while True:
    LED_CONTROLLER.all_off()

    # State is False when button is pressed (pull-up !)
    GPIO.wait_for_edge(BUTTON_PIN, GPIO.FALLING)
    sleep(0.2) # Button debounce
    print('Button pressed.')

    # Counting time elapsed since the button was pressed. Turn off device if it was held down for three seconds
    start_time = time()
    elapsed = 0
    while not GPIO.input(BUTTON_PIN) and elapsed <= OFF_HOLD_TIME:
        elapsed = time() - start_time
        sleep(0.01)

    if elapsed > OFF_HOLD_TIME:
        # Turning device off
        print(f'Button pressed for more than {OFF_HOLD_TIME} seconds. Turning off.')
        LED_CONTROLLER.all_on()
        os.system('sudo poweroff')

    else:
        print('Fetching data from lemet.fr')

        # Display cycle animation
        LED_CONTROLLER.cycle()

        try:
            # Fetching data
            full_results = get_next_buses(cfg.line_id, cfg.way, cfg.stop_id)

            # Case 1 : There are no departures anymore
            if not full_results['directions']:
                val1 = None
                val2 = None

            # Case 2 : There are one or more departures
            else:
                results = full_results['directions'][0]['passages']
                res1 = results[0]
                min1 = res1['minutes']
                tel1 = res1['TAD']
                val1 = (min1, tel1)

                # There are at least two buses
                if len(results) > 1:
                    res2 = results[1]
                    min2 = res2['minutes']
                    tel2 = res2['TAD']
                    val2 = (min2, tel2)

                # There is only one bus left
                else:
                    val2 = None

            # Display result for 10 seconds
            LED_CONTROLLER.display(val1, val2)
            sleep(10)

        except:
            # Something went wrong. Turn everything on to let the user know
            LED_CONTROLLER.all_on()
            sleep(5)
