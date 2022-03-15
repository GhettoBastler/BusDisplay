#!/usr/bin/env python

import threading
import RPi.GPIO as GPIO
from time import sleep


GPIO.setmode(GPIO.BCM)

SEGMENT_PINS = (2, 3, 4, 5, 6, 7, 8)
DIGIT_PINS = ((9, 10), (11, 12))
TEL_PINS = (13, 14)

DIGIT_CODES = {
    0: (True, True, True, True, True, True, False),
    1: (False, True, True, False, False, False, False),
    2: (True, True, False, True, True, False, True),
    3: (True, True, True, True, False, False, True),
    4: (False, True, True, False, False, True, True),
    5: (True, False, True, True, False, True, True),
    6: (True, False, True, True, True, True, True),
    7: (True, True, True, False, False, False, False),
    8: (True, True, True, True, True, True, True),
    9: (True, True, True, True, False, True, True),
    '-': (False, False, False, False, False, False, True),
    'H': (False, True, True, False, True, True, True),
}


class LEDController:

    def __init__(self, segment_pins=SEGMENT_PINS, digit_pins=DIGIT_PINS, tel_pins=TEL_PINS, delay=0.005):
        self.segment_pins = segment_pins
        self.digit_pins = digit_pins
        self.tel_pins = tel_pins
        self.delay=delay

        self.number1 = (8, 8)
        self.number2 = (8, 8)
        self.tel1 = True
        self.tel2 = True

        self._setup()

        self.status = 0

        self._cycle_idx = 0

        self.thread = threading.Thread(target=self._update_display, daemon=True)
        self.thread.start()


    def _setup(self):
        for pin in self.digit_pins[0] + self.digit_pins[1]:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

        for pin in self.segment_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)

        for pin in self.tel_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)


    def _display_one_digit(self, value, digit_pin):
        for i, pin in enumerate(self.segment_pins):
            if DIGIT_CODES[value][i]:
                GPIO.output(pin, GPIO.LOW)
            else:
                GPIO.output(pin, GPIO.HIGH)

        GPIO.output(digit_pin, GPIO.HIGH)


    def _display_number(self, number, digit_pins):
        for i, pin in enumerate(digit_pins):
            d = number[i]
            self._display_one_digit(d, pin)
            sleep(self.delay)
            GPIO.output(pin, GPIO.LOW)


    def _turn_all_off(self):
        for pin in self.digit_pins[0] + self.digit_pins[1]:
            GPIO.output(pin, GPIO.LOW)

        for pin in self.segment_pins:
            GPIO.output(pin, GPIO.HIGH)

        for pin in self.tel_pins:
            GPIO.output(pin, GPIO.LOW)


    def _update_display(self):
        while True:
            if self.status != 2:
                # Reset index for cycle animation
                self._cycle_idx = 0

            if self.status == 0:
                # Turn everything off
                self._turn_all_off()

            elif self.status == 1:
                # Display numbers
                self._display_number(self.number1, self.digit_pins[0])
                self._display_number(self.number2, self.digit_pins[1])

                if self.tel1:
                    GPIO.output(self.tel_pins[0], GPIO.HIGH)
                else:
                    GPIO.output(self.tel_pins[0], GPIO.LOW)

                if self.tel2:
                    GPIO.output(self.tel_pins[1], GPIO.HIGH)
                else:
                    GPIO.output(self.tel_pins[1], GPIO.LOW)

            elif self.status == 2:
                # Cycle animation
                # Turn telephone LEDs off
                GPIO.output(self.tel_pins[0], GPIO.LOW)
                GPIO.output(self.tel_pins[1], GPIO.LOW)

                # Display '-'
                for i, pin in enumerate(self.segment_pins):
                    # if DIGIT_CODES['-'][i]:
                    if i == self._cycle_idx:
                        GPIO.output(pin, GPIO.LOW)
                    else:
                        GPIO.output(pin, GPIO.HIGH)

                # Light all digits at the same time
                for pin in self.digit_pins[0] + self.digit_pins[1]:
                    GPIO.output(pin, GPIO.HIGH)

                sleep(0.1)
                self._cycle_idx = (self._cycle_idx + 1) % 6

                # OFF
                # for pin in self.digit_pins[0] + self.digit_pins[1]:
                #     GPIO.output(pin, GPIO.LOW)
                # sleep(1)

            else:
                # Light everything up
                GPIO.output(self.tel_pins[0], GPIO.HIGH)
                GPIO.output(self.tel_pins[1], GPIO.HIGH)

                self._display_number((8, 8), self.digit_pins[0])
                self._display_number((8, 8), self.digit_pins[1])


    def all_off(self):
        self.status = 0


    def all_on(self):
        self.status = 3


    def cycle(self):
        self.status = 2


    def _number_to_digits(self, number):
        if number >= 60:
            # Convert into hours
            val = number // 60   
            return (val, 'H')

        else:
            return tuple(map(int, '{:02}'.format(number)))


    def display(self, data1, data2=None):
        # Data should be a tuple of the form (minutes, TAD)
        if data1:
            self.number1 = self._number_to_digits(data1[0])
            self.tel1 = data1[1]
        else:
            self.number1 = ('-', '-')
            self.tel1 = False

        if data2:
            self.number2 = self._number_to_digits(data2[0])
            self.tel2 = data2[1]
        else:
            self.number2 = ('-', '-')
            self.tel2 = False
        

        self.status = 1
