class Message:
    def __init__(self, sender, receiver, header: dict, payload: dict={}):
        self.sender = sender
        self.receiver = receiver
        self.header = header
        self.payload = payload

    def get_payload(self):
        return self.payload
    
    def __str__(self):
        return f"From: {self.sender}\nTo: {self.receiver}\nPayload: {self.payload}"