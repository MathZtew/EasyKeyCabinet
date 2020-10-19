import os

langs = {}

def read_lang(file_name):
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
            tokens[1] = tokens[1].split(",")
            if len(tokens[1]) == 4:
                res[tokens[0]] = tokens[1]
            else:
                print("error reading config line", line)
                return
        else:
            print("error reading config line", line)
            return
    file.close()
    return res


def strings(name, lang, l1="", l2="", l3="", l4=""):
    ret = list.copy(langs[lang][name])
    if l1 != "":
        ret[0] = l1
    if l2 != "":
        ret[1] = l2
    if l3 != "":
        ret[2] = l3
    if l4 != "":
        ret[3] = l4
    return ret


langs["english"] = read_lang("english.lang")
langs["swedish"] = read_lang("swedish.lang")
