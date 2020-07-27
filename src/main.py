import oledlib as oled
import keylib as keys


def key_string(status):
    return "U" if not status else "L"


def write_status(key_status):
    first = key_string(key_status[0]) + " " + key_string(key_status[1]) + " " + key_string(key_status[2])
    second = key_string(key_status[3]) + " " + key_string(key_status[4]) + " " + key_string(key_status[5])
    third = key_string(key_status[6]) + " " + key_string(key_status[7]) + " " + key_string(key_status[8])
    oled.write_to_display(first, second, third, "")
    

if __name__ == "__main__":
    oled.write_to_display("Test", "test", "TESTTEST", "TestTest")

    key_status = [False, False, False, False, False, False, False, False, False]

    try:
        
        for i in range(9):
            oled.write_to_display("unlocked", "key", str(i), "")
            keys.unlock_key(i)
        
        oled.write_to_display("unlocked", "all keys", "", "")
        
        while True:
            for i in range(9):
                button_status = keys.button_status(i)
                if key_status[i] and button_status == 1:
                    keys.unlock_key(i)
                    key_status[i] = not key_status[i]
                    print(key_status)
                    write_status(key_status)
                elif (not key_status[i]) and button_status == 1:
                    keys.lock_key(i)
                    key_status[i] = not key_status[i]
                    print(key_status)
                    write_status(key_status)

    except KeyboardInterrupt:
        keys.clean_up()
        oled.clear_display()
