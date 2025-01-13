import json
class Message:
    def __init__(self, content_type: str, content: dict={}, sender: str=None):
        """
        Initialize a new message object.
        :param content_type: The type of content in the message (BK for Block, TX for transaction).
        :param content: The content of the message.
        :param sender: The sender of the message.
        """
        self.content_type = content_type
        self.content = content
        self.sender = sender

    def get_content(self):
        """
        Get the content of the message.
        """
        return self.content
    
    def get_content_type(self):
        """
        Get the content type of the message.
        """
        return self.content_type
    
    def get_sender(self):
        """
        Get the sender of the message.
        """
        return self.sender
    
    def to_dict(self) -> dict:
        """
        Converts the Message object to a dictionary.

        :Returns: (dict) A dictionary representation of the message.
        """
        return {
            "sender": self.sender,
            "content_type": self.content_type, 
            "content": self.content
            }
    
    def to_json(self) -> str:
        """
        Converts the Message object to a JSON string.

        Returns: (str) A JSON representation of the message.
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: dict, sender: str=None):
        """
        Creates a Message object from a dictionary.

        :param: data (dict): A dictionary containing the message data.

        :Returns: (Message) The constructed Message object.
        """
        if sender:
            return cls(data["content_type"], data["content"], sender)
        return cls(data["content_type"], data["content"])
    
    @classmethod
    def from_json(cls, json_data: str):
        """
        Creates a Message object from a JSON string.

        :param: json_data (str): A JSON string containing the message data.

        :Returns: (Message) The constructed Message object.
        """
        try:
            data = json.loads(json_data)
            if not isinstance(data, dict):
                raise ValueError("JSON data is not a valid dictionary")
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {e}")

    @classmethod
    def generate_start_message(cls, shard_name: str, epoch: int, node_name: str):
        """
        Generate a START message.
        """
        return Message(content_type="CONTROL", content={
            "action": "START",
            "shard": shard_name,
            "epoch": epoch
        }, sender=node_name)
    
    @classmethod
    def generate_stop_message(cls, shard_name: str, epoch: int, node_name: str):
        """
        Generate a STOP message.
        """
        return Message(content_type="CONTROL", content={
            "action": "STOP",
            "shard": shard_name,
            "epoch": epoch
        }, sender=node_name)

    
    def __str__(self):
        """
        Get a string representation of the message.
        """
        return f"Content Type: {self.content_type}\nContent: {self.content}"