import oledlib as oled
import keylib as keys
import time
import requests

import string

from evdev import InputDevice
from select import select

from datetime import datetime

cardreader_input = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"

NUM_OF_KEYS = 9
LOOP_WAIT = 0.1
V_NUMBER = "0.1"
MESSAGE_STATUS_TIME = 2
WAIT_FOR_PRESS = 20

def read_options(file_name):
    """
    Read config file in the same directory as the script file.
    """
    file = open(file_name, 'r')
    lines = file.readlines()
    res = {}
    for line in lines:
        line = line.replace("\n", "")
        tokens = line.split("=", 1)
        if (len(tokens) == 2):
            res[tokens[0]] = tokens[1]
        else:
            print("error reading config line", line)
    file.close()
    return res

def key_string(status):
    """ Status in string form for keys locked status """
    return "U" if not status else "L"


def write_status(key_status):
    """
    Print out the status of all keys on the oled display.
    """
    first = key_string(key_status[0]) + " " + key_string(key_status[1]) + " " + key_string(key_status[2])
    second = key_string(key_status[3]) + " " + key_string(key_status[4]) + " " + key_string(key_status[5])
    third = key_string(key_status[6]) + " " + key_string(key_status[7]) + " " + key_string(key_status[8])
    oled.write_to_display(first, second, third, "")


def wait_for_value(button, value):
    """
    Waiting for a value for a button corresponding to a key id.
    """
    while keys.button_status(button) != value:
        time.sleep(LOOP_WAIT)


def choose_a_key(wait_time):
    """
    Wait until a key is pressed down, return the pressed id.
    
    if wait_time is exceeded id -1 is returned.
    """
    # Change to a time interval
    loops = wait_time / LOOP_WAIT

    while loops > 0 or wait_time < 0:
        for i in range(NUM_OF_KEYS):
            if keys.button_status(i) == 1:
                return i
        time.sleep(LOOP_WAIT)
        loops -= 1

    return -1


def get_card_nr(dev):
    """
    Read the card reader in the place dev.
    """
    res = ""
    while True:
        r,w,x = select([dev], [], [])
        for event in dev.read():
            if event.type==1 and event.value==1:
                #print( keys[ event.code ] )
                if cardreader_input[event.code] in string.digits:
                    res += cardreader_input[event.code]
                else:
                    return res


def lock_chosen_key(key_status, wait_time):
    """
    lock/unlock the key that is pressed.

    Prints error message on oled if no key is chosen within time limit.
    """
    pressed_key = choose_a_key(wait_time)
    # False == locked
    if pressed_key != -1:
        if not key_status[pressed_key]:
            keys.unlock_key(pressed_key)
        else:
            keys.lock_key(pressed_key)
        oled.write_to_display("", "Release", "the key", "")
        wait_for_value(pressed_key, 0)
        key_status[pressed_key] = not key_status[pressed_key]
    else:
        oled.write_to_display("No key","chosen","within", "time limit")
        time.sleep(MESSAGE_STATUS_TIME)
    #write_status(key_status)
    

def get_key_status(token, key_list_endpoint):
    """
    Get the status of the keys from the remote API.
    
    Returns the locked statuses of the keys, 
    as well as the statuses in a dictionary.
    """
    key_status = [False, False, False, False, False, False, False, False, False]
    key_api_status = {}
        
    response_keys = requests.get(key_list_endpoint, headers={"Authorization":"Token " + token})
    
    keylist = response_keys.json()
    i = 1
    for i in range(len(keylist)):
        msg_id = None
        # Lock the key if status is away
        if keylist[i].get("status") != None:
            key_status[keylist[i].get("order")] = keylist[i].get("status").get("taken_successfully") == True
            msg_id = keylist[i].get("status").get("id")
        else:
            key_status[keylist[i].get("order")] = False
        keylist[i]["id"] = i
        key_api_status[keylist[i].get("order")] = keylist[i]
        
    return key_status, key_api_status


def take_key(key_log_entry_list_endpoint, key_api_status, key_status, token):
    """
    Scan the LIU-ID and registers a key press.
    
    Locks/unlocks the key if the user exists.
    
    Sends corresponding data to the API.
    """
    
    #oled.write_to_display("Scan","LiU-ID","","")
    oled.clear_display()
    card_nr = get_card_nr(dev)
    oled.write_to_display("Press","key","","")
    pressed_key = choose_a_key(WAIT_FOR_PRESS)
    
    # The key was not pressed within time limit
    if pressed_key == -1:
        oled.write_to_display("No key","chosen","within", "time limit")
        time.sleep(MESSAGE_STATUS_TIME)
        return False, False
    
    # The key was not in the list from the API
    if key_api_status.get(pressed_key) == None:
        oled.write_to_display("Key not","in system","", "")
        time.sleep(MESSAGE_STATUS_TIME)
        return False, False
    
    # Fill in the required fields
    content = {
        "key_id": key_api_status.get(pressed_key).get("id"),
        "taken_by_id": "",
        "taken_at": None,
        "taken_successfully": False,
        "returned_by_id": "",
        "returned_at": None,
        "returned_successfully": False
        }
    
    oled.write_to_display("Nyckel:", key_api_status.get(pressed_key).get("name"), "", "")
    
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%dT%H:%M")
    
    is_taking = not key_status[pressed_key]
    
    msg_id = 0
    response = ""
    response_json = ""
    
    # If the key is locked fill in the appropriate fields
    if is_taking:
        content["taken_successfully"] = False
        content["taken_by_id"] = "card_id:" + card_nr
        content["taken_at"] = dt_string
        response = requests.post(key_log_entry_list_endpoint, headers = {"Authorization":"Token " + token}, data=content)
        response_json = response.json()
        msg_id = response_json["id"]
        
    else:
        content = {}
        content["returned_successfully"] = False
        content["returned_by_id"] = "card_id:" + card_nr
        content["returned_at"] = dt_string
        msg_id = key_api_status.get(pressed_key).get("status").get("id")
        response = requests.patch(key_log_entry_list_endpoint + "/" + str(msg_id) + "/", content, headers = {"Authorization":"Token " + token})
        response_json = response.json()
        
    id_exist = False
    
    # Check that the API has returned a user
    for i in range(2):
        field_check = "taken_by" if is_taking else "returned_by"
        if response_json.get(field_check) == None:
            oled.write_to_display("Please","scan card","again","")
            card_nr = get_card_nr(dev)
            
            content[field_check + "_id"] = "card_id:" + card_nr
            
            # Send again
            if is_taking:
                response = requests.post(key_log_entry_list_endpoint, headers = {"cookie":cookie, "referer": referer}, data=content)
            else:
                response = requests.patch(key_log_entry_list_endpoint + "/" + str(msg_id) + "/", content, headers = {"Authorization":"Token " + token})
            response_json = response.json()
        else:
            id_exist = True
            break
        
    # If the check was not successfull
    if not id_exist:
        oled.write_to_display("User","not","registered","")
        return False, False
    
    if is_taking:
        content = {}
        oled.write_to_display("Unlocking","","","")
        keys.unlock_key(pressed_key)
        key_status[pressed_key] = True
        content["taken_successfully"] = True
        response = requests.patch(key_log_entry_list_endpoint + "/" + str(msg_id) + "/", data=content, headers = {"Authorization":"Token " + token})
        
    else:
        content = {}
        oled.write_to_display("Locking","","","")
        keys.lock_key(pressed_key)
        key_status[pressed_key] = False
        content["returned_successfully"] = True
        response = requests.patch(key_log_entry_list_endpoint + "/" + str(msg_id) + "/", content, headers = {"Authorization":"Token " + token})
    
    return pressed_key, content    


if __name__ == "__main__":   
    options = read_options("config.conf")

    try:
        dev_path = options["input_device"]
        key_list_endpoint = options["key_list_endpoint"]
        key_log_entry_list_endpoint = options["key_log_entry_list_endpoint"]
        organization=options["organization"]
        xcsrftoken=options["xcsrftoken"]
        token=options["token"]
    except KeyError as inst:
        print(inst.args, "not in config file")
        exit(0)
        
    oled.write_to_display(organization, "Nyckelskåp", "V " + V_NUMBER, "")
    time.sleep(MESSAGE_STATUS_TIME)
        
    dev = InputDevice(dev_path)
    key_status, key_api_status = get_key_status(token, key_list_endpoint)
    
    try:
        # Lock/unlock keys with information from the website
        for i in range(NUM_OF_KEYS):
            if key_status[i]:
                oled.write_to_display("unlocked", "key", str(i), "")
                keys.unlock_key(i)
            else:
                oled.write_to_display("locked", "key", str(i), "")
                keys.lock_key(i)

        oled.write_to_display("", "all keys", "unlocked/", "locked")
        time.sleep(MESSAGE_STATUS_TIME)
        
        while True:
            key_placement, status = take_key(key_log_entry_list_endpoint, key_api_status, key_status, token)
            new_key_status, key_api_status = get_key_status(token, key_list_endpoint)
            
            for i in range(len(key_status)):
                if key_status[i] != new_key_status[i]:
                    print("Key status in id", i, "not updated in API")

    except KeyboardInterrupt:
        keys.clean_up()
        oled.clear_display()
