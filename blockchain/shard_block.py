import json
import hashlib
from typing import List
from transaction.transaction import Transaction

class ShardBlock:
    def __init__(self, miner_id, merkle_root, timestamp, transactions: List[Transaction]):  
        """
        Initialize a new block.
        """
        self.miner_id = miner_id
        self.timestamp = timestamp
        self.merkle_root = merkle_root
        self.transactions = transactions

    @classmethod
    def from_dict(cls, block_data):
        """
        Convert JSON Data into an instance of a Block class.
        """
        transactions = [
            Transaction.from_dict(tx) if isinstance(tx, dict) else 
            tx for tx in block_data.get("transactions", [])
        ]
        return cls(miner_id = block_data["miner_id"],
                timestamp = block_data["timestamp"], 
                merkle_root = block_data["merkle_root"],
                transactions = transactions,
                )

    def to_dict(self):
        """
        Convert the block object into a dictionary for JSON serialization.
        """
        return {
                "miner_id":self.miner_id,
                "timestamp":self.timestamp,
                "merkle_root":self.merkle_root,
                "transactions":
                    [tx.to_dict() if hasattr(tx, "to_dict") 
                     else tx for tx in self.transactions],
                }
  
    def compute_hash(self):
        """
        Compute the hash of the block.
        """
        block_content = {
                "miner_id":self.miner_id,
                "timestamp":self.timestamp,
                "merkle_root":self.merkle_root,
                "transactions":self.transactions,
            }
        
        encoded_block_string = json.dumps(block_content, sort_keys=True).encode()
        block_hash = hashlib.sha256(encoded_block_string).hexdigest()
        return block_hash