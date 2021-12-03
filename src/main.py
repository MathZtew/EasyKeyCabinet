import oledlib as oled
import keylib as keys
import time
import requests
import os

import string

from evdev import InputDevice
from select import select

from datetime import datetime

import signal

import read_HID
import oled_strings

NUM_OF_KEYS = 9
LOOP_WAIT = 0.1
V_NUMBER = "0.1"
MESSAGE_STATUS_TIME = 2
WAIT_FOR_PRESS = 20
LANG="swedish"


def read_options(file_name):
    """
    Read config file in the same directory as the script file.
    """
    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    rel_path = file_name
    abs_file_path = os.path.join(script_dir, rel_path)
    file = open(abs_file_path, 'r')
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
    forever = wait_time == -1
    # Change to a time interval
    loops = wait_time / LOOP_WAIT

    while (loops > 0 or wait_time < 0) or forever:
        for i in range(NUM_OF_KEYS):
            if keys.button_status(i) == 1:
                return i
        time.sleep(LOOP_WAIT)
        loops -= 1

    return -1


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
        oled.wltd(oled_strings.strings("release_key", LANG))
        wait_for_value(pressed_key, 0)
        key_status[pressed_key] = not key_status[pressed_key]
    else:
        oled.wltd(oled_strings.strings("key_not_chosen_time", LANG))
        time.sleep(MESSAGE_STATUS_TIME)
    #write_status(key_status)
    

def get_key_status(token, key_list_endpoint):
    """
    Get the status of the keys from the remote API.
    
    Returns the locked statuses of the keys, 
    as well as the statuses in a dictionary.
    """
    key_status = [False for i in range(NUM_OF_KEYS)]
    key_api_status = {}
        
    response_keys = requests.get(key_list_endpoint, headers={"Authorization":"Token " + token})
    
    keylist = response_keys.json()
    
    i = 1
    for i in range(len(keylist)):
        msg_id = None
        # Lock the key if status is away
        status = keylist[i].get("status")
        if status != None:
            key_status[keylist[i].get("order")] = status.get("taken_successfully") == True
            msg_id = status.get("id")
        else:
            key_status[keylist[i].get("order")] = False
        key_api_status[keylist[i].get("order")] = keylist[i]
        
    print(key_api_status)
        
    return key_status, key_api_status


def is_locked(key_status, index):
    """
    Checks whether a key is currently locked.
    """
    return not key_status[index]


def today_date():
    """
    Gets today's date in correct format for sending to the server.
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%dT%H:%M")


def take_key(key_log_entry_list_endpoint, key_api_status, key_status, token):
    """
    Scan the ID and registers a key press.
    
    Locks/unlocks the key if the user exists.
    
    Sends corresponding data to the API.
    """
    
    oled.clear_display()
    # Pressing a key will start it
    pressed_key = choose_a_key(-1)
    
    # The key was not in the list from the API
    if key_api_status.get(pressed_key) == None:
        oled.wltd(oled_strings.strings("no_key", LANG))
        time.sleep(MESSAGE_STATUS_TIME)
        return False, False
    
    oled.wltd(oled_strings.strings("scan_auth", LANG))
    
    id_string = read_HID.read_input(WAIT_FOR_PRESS, dev)
    
    if id_string == -1:
        oled.wltd(oled_strings.strings("no_auth", LANG))
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
    
    # Write out the given name of the key
    oled.wltd(oled_strings.strings("key_name", LANG, l2=key_api_status.get(pressed_key).get("name")))
    
    # Get date and time
    dt_string = today_date()
    
    # Check whether the key is being taken or returned
    is_taking = is_locked(key_status, pressed_key)
    
    # Initialise variables
    msg_id = 0
    response_json = ""
    
    # If the key is locked fill in the appropriate fields
    if is_taking:
        content["taken_successfully"] = False
        content["taken_by_id"] = "auto:" + id_string
        content["taken_at"] = dt_string
        response_json = post_api(key_log_entry_list_endpoint, content, token)
        msg_id = response_json.get("id")
        if msg_id == None:
            oled.wltd(oled_strings.strings("com_error", LANG))
            return
    
    # If the key is unlocked
    else:
        content = {}
        content["returned_successfully"] = False
        content["returned_by_id"] = "auto:" + id_string
        content["returned_at"] = dt_string
        msg_id = key_api_status.get(pressed_key).get("status").get("id")
        response_json = patch_api(key_log_entry_list_endpoint, msg_id, content, token)
    
    # Check that the API has returned a user
    response_json = retry_sending(is_taking, dev, key_log_entry_list_endpoint, msg_id, token, content, response_json)
    
    # If the check was not successfull
    if not response_json:
        oled.wltd(oled_strings.strings("user_not_reg", LANG))
        return False, False
    
    # Clean content to prepare for patch request
    content = {}
    
    # Unlock and send successfull to the API
    if is_taking:
        oled.wltd(oled_strings.strings("uing_key", LANG, l2=key_api_status.get(pressed_key).get("name")))
        keys.unlock_key(pressed_key)
        key_status[pressed_key] = True
        content["taken_successfully"] = True
        
    # Lock and send successfull to the API
    else:
        oled.wltd(oled_strings.strings("press_key", LANG, l3=key_api_status.get(pressed_key).get("name")))
        wait_for_value(pressed_key, 1)
        oled.wltd(oled_strings.strings("ling_key", LANG, l2=key_api_status.get(pressed_key).get("name")))
        keys.lock_key(pressed_key)
        key_status[pressed_key] = False
        content["returned_successfully"] = True
        
    patch_api(key_log_entry_list_endpoint, msg_id, content, token)


def retry_sending(is_taking, dev, endpoint, msg_id, token, content, response_json):
    """
    Retry sending the card number if no user was registered.
    
    returns False if no user was detected from the API.
    """
    
    field_check = "taken_by" if is_taking else "returned_by"
    for i in range(2):
        if response_json.get(field_check) == None:
            oled.wltd(oled_strings.strings("auth_again", LANG))
            id_string = read_HID.read_input(WAIT_FOR_PRESS, dev)
            
            content[field_check + "_id"] = "auto:" + id_string
            
            # Send again
            if is_taking:
                response_json = patch_api(endpoint, msg_id, content, token)
            else:
                response_json = patch_api(endpoint, msg_id, content, token)
        else:
            return response_json
    
    # Check response
    if response_json.get(field_check) != None:
        return response_json
        
    return False


def patch_api(endpoint, msg_id, content, token):
    """ Send a patch request to the given log id with the supplied content """
    response = requests.patch(endpoint + "/" + str(msg_id) + "/", content, headers = {"Authorization":"Token " + token})
    return response.json()


def post_api(endpoint, content, token):
    """ Post a new request to the API """
    response = requests.post(endpoint, content, headers = {"Authorization":"Token " + token})
    return response.json()


def terminateProcess(signalNumber, frame):
    """ Clean up and terminate the program """
    keys.clean_up()
    oled.clear_display()
    exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, terminateProcess)
    options = read_options("config.conf")

    # Parse all the options from the config
    try:
        dev_path = options["input_device"]
        key_list_endpoint = options["key_list_endpoint"]
        key_log_entry_list_endpoint = options["key_log_entry_list_endpoint"]
        organization=options["organization"]
        token=options["token"]
    except KeyError as inst:
        print(inst.args, "not in config file")
        terminateProcess(None, None)
       
    # Print welcome message
    #oled.write_to_display(organization, "Key cabinet", "V " + V_NUMBER, "")
    oled.wltd(oled_strings.strings("welcome", LANG, l1=organization, l3="V " + V_NUMBER))
    time.sleep(MESSAGE_STATUS_TIME)
        
    # Startup and messages to the oled screen
    oled.wltd(oled_strings.strings("looking_for_card", LANG))
    dev = InputDevice(dev_path)
    oled.wltd(oled_strings.strings("get_key_status", LANG))
    
    key_status = False
    key_api_status = False
    
    # Try to get the information from the API 10 times
    for i in range(10):
        try:
            key_status, key_api_status = get_key_status(token, key_list_endpoint)
            break
        except:
            oled.wltd(oled_strings.strings("API_error", LANG, l4 = "5s " + str(i + 1) + "/10"))
            time.sleep(5)
    
    if key_status == False:
        exit(0)
            
    oled.wltd(oled_strings.strings("start_main", LANG))
    
    try:
        # Lock/unlock keys with information from the website
        for i in range(NUM_OF_KEYS):
            name = ""
            if i in key_api_status.keys():
                name = key_api_status.get(i).get("name")
            if key_status[i]:
                oled.wltd(oled_strings.strings("u_key", LANG, l3=str(i), l4=name))
                keys.unlock_key(i)
            else:
                oled.wltd(oled_strings.strings("l_key", LANG, l3=str(i), l4=name))
                keys.lock_key(i)

        oled.wltd(oled_strings.strings("keys_ul", LANG))
        time.sleep(MESSAGE_STATUS_TIME)
        
        while True:
            
            take_key(key_log_entry_list_endpoint, key_api_status, key_status, token)
            new_key_status, key_api_status = get_key_status(token, key_list_endpoint)
            
            for i in range(len(key_status)):
                if key_status[i] != new_key_status[i]:
                    print("Key status in id", i, "not updated in API")

    except KeyboardInterrupt:
        terminateProcess(None, None)

