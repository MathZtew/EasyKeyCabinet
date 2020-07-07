import oledlib as oled
import keylib as keys

if __name__ == "__main__":
    oled.write_to_display("Test", "test", "TESTTEST", "TestTest")

    try:
        a = False
        while True:
            keys.unlock_key(0)
            oled.write_to_display("unlocked", "", "", "")

            while keys.button_status(0) == 0:
                pass

            keys.lock_key(0)
            oled.write_to_display("locked", "", "", "")

            while keys.button_status(0) == 0:
                pass
    except KeyboardInterrupt:
        keys.clean_up()
