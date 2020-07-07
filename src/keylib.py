import RPi.GPIO as GPIO
import time

servoPIN = 17
buttonPIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)
GPIO.setup(buttonPIN, GPIO.IN)

p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz


keys = [p] # array with all keys
buttons = [buttonPIN]


def set_degrees(pos):
    value = float(pos * 5)
    value = value / 180
    value += 5
    return value


def lock_key(key):
    pwm = keys[key]
    pwm.start(set_degrees(0))
    time.sleep(1)
    p.start(0)


def unlock_key(key):
    pwm = keys[key]
    pwm.start(set_degrees(180))
    time.sleep(1)
    p.start(0)


def button_status(key):
    return GPIO.input(buttons[key])


def clean_up():
    for servo in keys:
        servo.stop()
    GPIO.cleanup()


p.start(set_degrees(0)) # Initialization
