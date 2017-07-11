#! /usr/bin/python3

import schedule
import time
import requests
import Adafruit_ADS1x15
import RPi.GPIO as GPIO


def post(m1, m2):
    '''
    Post data to sparkfun data store.
    '''
    try:
        payload={'private_key': 'RnBEyBd2bwI0JWbgPY2K', 'm_1': m1, 'm_2': m2}
        r = requests.get('http://data.sparkfun.com/input/YDdp9doqGXT9GpWXoYA8/', params=payload)
        return  r.status_code
    except:
        return 0


GPIO.setmode(GPIO.BCM)

# Create an ADS1115 ADC (16-bit) instance.
adc = Adafruit_ADS1x15.ADS1115(0x48, busnum=1)

moisture_enable_pin = 13

motor_1_pin = 19 # Tomaros
motor_2_pin = 26 # Cucumbers

GPIO.setup(motor_1_pin, GPIO.OUT)
GPIO.setup(motor_2_pin, GPIO.OUT)
GPIO.setup(moisture_enable_pin, GPIO.OUT)

GPIO.output(moisture_enable_pin, GPIO.LOW)
GPIO.output(motor_1_pin, GPIO.LOW)
GPIO.output(motor_2_pin, GPIO.LOW)

GAIN = 1


def measure():
    # Enable Sensors
    GPIO.output(moisture_enable_pin, GPIO.HIGH)
    time.sleep(0.5)
    # Read all the ADC channel values in a list.
    values = [0]*4
    for i in range(2):
        # Read the specified ADC channel using the previously set gain value.
        values[i] = adc.read_adc(i, gain=GAIN)

    # Disable sensor
    GPIO.output(moisture_enable_pin, GPIO.LOW)
    # Print the ADC values.
    values[2] = post(values[0], values[1])
    print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*values))


def feed(circles, pin):
    '''
    Enable motor for a 3 minutes,
    With some sleep between to cooldown device.
    '''
    seconds = 30
    for c in range(circles):
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(3*seconds)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(1*seconds)

def feed_tomatoes():
    print("Feeding tomatoes")
    feed(7, motor_1_pin)

def feed_cucumbers():
    print("Feeding cucumbers")
    feed(5, motor_2_pin)


schedule.every().day.at("19:00").do(feed_tomatoes)
schedule.every().day.at("20:00").do(feed_tomatoes)
schedule.every().day.at("21:00").do(feed_tomatoes)

schedule.every().day.at("06:00").do(feed_cucumbers) 
schedule.every().day.at("07:00").do(feed_cucumbers)
schedule.every().day.at("08:00").do(feed_cucumbers)

schedule.every(5).minutes.do(measure)

print("Started")

while True:
    schedule.run_pending()
    time.sleep(1)
