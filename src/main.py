import oledlib as oled
import keylib as keys
import time

NUM_OF_KEYS = 9
LOOP_WAIT = 0.1
V_NUMBER = "0.1"


def key_string(status):
    return "U" if not status else "L"


def write_status(key_status):
    first = key_string(key_status[0]) + " " + key_string(key_status[1]) + " " + key_string(key_status[2])
    second = key_string(key_status[3]) + " " + key_string(key_status[4]) + " " + key_string(key_status[5])
    third = key_string(key_status[6]) + " " + key_string(key_status[7]) + " " + key_string(key_status[8])
    oled.write_to_display(first, second, third, "")
    
    
def wait_for_value(button, value):
    while keys.button_status(button) != value:
        time.sleep(LOOP_WAIT)
        

def choose_a_key():
    # Change to a time interval
    while True:
        for i in range(NUM_OF_KEYS):
            if keys.button_status(i) == 1:
                return i
        time.sleep(LOOP_WAIT)
            

if __name__ == "__main__":
    oled.write_to_display("D-sektionen", "Nyckelskåp", "V" + V_NUMBER, "")

    key_status = [False, False, False, False, False, False, False, False, False]

    try:
        
        for i in range(NUM_OF_KEYS):
            oled.write_to_display("unlocked", "key", str(i), "")
            keys.unlock_key(i)
        
        oled.write_to_display("unlocked", "all keys", "", "")
        
        while True:
            pressed_key = choose_a_key()
            if key_status[pressed_key]:
                keys.unlock_key(pressed_key)
            else:
                keys.lock_key(pressed_key)
            key_status[pressed_key] = not key_status[pressed_key]
            oled.write_to_display("", "Release", "the key", "")
            wait_for_value(pressed_key, 0)
            write_status(key_status)

    except KeyboardInterrupt:
        keys.clean_up()
        oled.clear_display()
