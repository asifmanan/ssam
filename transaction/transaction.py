import hashlib
import json

class Transaction:
    def __init__(self, sender, recipient, amount, timestamp, metadata, signature=None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = timestamp
        self.metadata = metadata
        self.signature = signature

    def to_dict(self):
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "signature": self.signature,
        }
    
    @classmethod
    def from_dict(cls,tx_data: dict):
        sender = tx_data["sender"]
        recipient = tx_data["recipient"]
        amount = tx_data["amount"]
        timestamp = tx_data["timestamp"]
        metadata = tx_data["metadata"]
        signature = tx_data["signature"]
        tx = Transaction(sender, recipient, amount, timestamp, metadata, signature)
        return tx
    
    def hash_transaction(self):
        tx_hash = self.calculate_hash()
        self.signature = tx_hash

    def calculate_hash(self):
        transaction_data = self.to_dict()
        transaction_data["signature"] = None
        hash_object = hashlib.sha256(json.dumps(transaction_data, sort_keys=True).encode('utf-8'))
        return hash_object.hexdigest()