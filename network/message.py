import json
class Message:
    def __init__(self, content_type: str, content: dict={}):
        """
        Initialize a new message object.
        :param content_type: The type of content in the message (BK for Block, TX for transaction).
        :param content: The content of the message.
        """
        self.content_type = content_type
        self.content = content

    def get_content(self):
        return self.content
    
    def get_content_type(self):
        return self.content_type
    
    def to_dict(self) -> dict:
        """
        Converts the Message object to a dictionary.

        Returns:
        dict: A dictionary representation of the message.
        """
        return {
            "content_type": self.content_type, 
            "content": self.content
            }
    
    def to_json(self) -> str:
        """
        Converts the Message object to a JSON string.

        Returns:
        str: A JSON representation of the message.
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: dict):
        """
        Creates a Message object from a dictionary.

        Args:
        data (dict): A dictionary containing the message data.

        Returns:
        Message: The constructed Message object.
        """
        return cls(data["content_type"], data["content"])
    
    @classmethod
    def from_json(cls, json_data: str):
        """
        Creates a Message object from a JSON string.

        Args:
        data (str): A JSON string containing the message data.

        Returns:
        Message: The constructed Message object.
        """
        data = json.loads(json_data)
        return cls.from_dict(data)
    
    def __str__(self):
        return f"Content Type: {self.content_type}\nContent: {self.content}"