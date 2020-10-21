class Key:
    def __init__(self, id, name, order):
        self.id = id
        self.name = name
        self.order = order
        self.status = None


    def add_status(self, status):
        self.status = status


    def to_dict(self):
        status = self.status.to_dict() if self.status != None else None
        return {"id": self.id, "name": self.name, "status": status, "order": self.order}
