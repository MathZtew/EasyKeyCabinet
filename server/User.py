class User:
    def __init__(self, id, username, first_name, last_name):
        self.id = id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.pretty_name = first_name + " " + last_name
        self.card_nr = ""
        self.long_id = ""


    def set_identifiers(self, card="", long_id=""):
        self.card_nr = card if card != "" and type(card) == str else self.card_nr
        self.long_id = long_id if long_id != "" and type(long_id) == str else self.card_nr


    def is_user(self, identifier):
        return identifier == self.card_nr or identifier == self.long_id


    def __getattr__(self, attr):
        return self[attr]

    def to_dict(self):
        return {"id": self.id,
                "username": self.username,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "pretty_name": self.pretty_name}
