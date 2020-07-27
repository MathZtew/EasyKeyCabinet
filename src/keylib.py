import RPi.GPIO as GPIO
import time

servoPINs = [4, 5, 6, 7, 8, 9, 10, 11, 12]
buttonPINs = [13, 14, 15, 16, 17, 18, 19, 20, 21] 
GPIO.setmode(GPIO.BCM)

for servoPIN in servoPINs:
    GPIO.setup(servoPIN, GPIO.OUT)
    
for buttonPIN in buttonPINs:
    GPIO.setup(buttonPIN, GPIO.IN)

keys = [] # array with all servos

for servoPIN in servoPINs:
    p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
    keys.append(p)
print(keys)


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
    return GPIO.input(buttonPINs[key])


def clean_up():
    for servo in keys:
        servo.stop()
    GPIO.cleanup()
