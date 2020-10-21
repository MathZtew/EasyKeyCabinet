KEYS = ["id",
        "taken_by",
        "taken_at",
        "taken_successfully",
        "returned_by",
        "returned_at",
        "returned_successfully"]

from User import User

import datetime
date_format = "%Y-%m-%dT%H:%M"


class Keylog:
    def __init__(self, id, key_id):
        self.id = id
        self.taken_by = None
        self.taken_at = None
        self.taken_successfully = False
        self.returned_by = None
        self.returned_at = None
        self.returned_successfully = False
        self.key_id = key_id


    def take_key(self, user, time, successfull):
        self.taken_by = user
        self.taken_at = time
        self.taken_successfully = successfull


    def return_key(self, user, time, successfull):
        self.returned_by = user
        self.returned_at = time
        self.returned_successfully = successfull


    def change(self, key, value):
        if key == "taken_by":
            if type(value) == User:
                self.taken_by = value
        if key == "taken_at":
            if type(value) == str:
                try:
                    datetime.datetime.strptime(value, date_format)
                    self.taken_at = value
                except ValueError:
                    pass
        if key == "taken_successfully":
            if type(value) == bool:
                self.taken_successfully = value
        if key == "returned_by":
            if type(value) == User:
                self.returned_by = value
        if key == "returned_at":
            if type(value) == str:
                try:
                    datetime.datetime.strptime(value, date_format)
                    self.taken_at = value
                except ValueError:
                    pass
        if key == "returned_successfully":
            if type(value) == bool:
                self.returned_successfully = value
        print(key, value)
        print(self.to_dict())



    def to_dict(self):
        taken_by = None if self.taken_by == None else self.taken_by.to_dict()
        returned_by = None if self.returned_by == None else self.returned_by.to_dict()
        return {"id": self.id,
                "taken_by": taken_by,
                "taken_at": self.taken_at,
                "taken_successfully": self.taken_successfully,
                "returned_by": returned_by,
                "returned_at": self.returned_at,
                "returned_successfully": self.returned_successfully}
