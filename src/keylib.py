import RPi.GPIO as GPIO
import time

servoPIN = 17
buttonPIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)
GPIO.setup(buttonPIN, GPIO.IN)

def set_degrees(pos):
    value = float(pos * 5)
    value = value / 180
    value += 5
    print(pos, value)
    return value


def lock_key(pwm):
    pwm.start(set_degrees(0))
    time.sleep(1)
    p.start(0)

    
def unlock_key(pwm):
    pwm.start(set_degrees(180))
    time.sleep(1)
    p.start(0)


p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
p.start(set_degrees(0)) # Initialization
try:
    a = False
    while True:
        unlock_key(p)
        print("unlocked")
        
        while GPIO.input(buttonPIN) == 1:
            pass
        
        lock_key(p)
        print("locked")
        
        while GPIO.input(buttonPIN) == 1:
            pass
except KeyboardInterrupt:
    p.stop()
    GPIO.cleanup()

