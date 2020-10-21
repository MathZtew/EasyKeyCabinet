from Key import Key
from Keylog import Keylog
from User import User


def update_statuses():
    updated_keys = []
    for keylog in keylogs[::-1]:
        if keylog.taken_successfully and not keylog.returned_successfully and not keylog.key_id in updated_keys:
            print("updating key", keylog.key_id)
            keys[keylog.key_id].add_status(keylog)
            updated_keys.append(keylog.key_id)
        if len(updated_keys) == len(keys):
            break
    for key in keys.keys():
        print("checking key", keylog.key_id, updated_keys)
        if not key in updated_keys:
            keys[key].add_status(None)



def get_user(id):
    for user in users.values():
        if user.is_user(id):
            print("found:user")
            return user
    return False


def get_keys():
    return [key.to_dict() for key in keys.values()]


def get_log(log_id):
    return keylogs[log_id].to_dict() if keylogs[log_id] != None else None


def change_log(log_id, log_content):
    log = keylogs[log_id]
    print(log_content)
    if log == None:
        return
    for key, value in log_content.items():
        if key == "taken_by_id" or key == "returned_by_id":
            user = False
            if value.find("auto:") != -1:
                print(value[5:])
                user = get_user(value[5:])
                if user:
                    log.change(key[0:-3], user)
        else:
            log.change(key, value)
    update_statuses()
    return log.to_dict()

def new_log(new_log_content):
    if (new_log_content["key_id"] in keys.keys()):
        log = Keylog(len(keylogs), new_log_content["key_id"])
        keylogs.append(log)

        return change_log(log.id, new_log_content)
    return "Key id not in system"


keys = {}
users = {}
keylogs = []

keys[1] = Key(1, "Test", 0)
users[1] = User(1, "P1", "Person", "Persson")
users[1].set_identifiers(card="2345", long_id="1234")

log = Keylog(len(keylogs), 1)
log.take_key(users[1], "now", True)

#log.take_key(users[1], "now", True)

keylogs.append(log)

update_statuses()
