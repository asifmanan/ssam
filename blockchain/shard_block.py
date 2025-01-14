import json
import hashlib
from typing import List
from transaction.transaction import Transaction

class ShardBlock:
    def __init__(self, miner_numeric_id, miner_node_name, merkle_root,timestamp, transactions: List[Transaction], nonce: int=0, nbits: str="0x1f00ffff"):  
        """
        Initialize a new block.
        :param miner_numeric_id: The numeric ID of the miner.
        :param merkle_root: The Merkle root of the transactions.
        :param timestamp: The timestamp of the block.
        """
        self.miner_numeric_id = miner_numeric_id
        self.miner_node_name = miner_node_name
        self.timestamp = timestamp
        self.merkle_root = merkle_root
        self.transactions = transactions
        self.nbits = nbits
        self.nonce = nonce

    @classmethod
    def from_dict(cls, block_data):
        """
        Convert JSON Data into an instance of a Block class.
        :param block_data: The JSON data to be converted into a block.
        """
        transactions = [
            Transaction.from_dict(tx) if isinstance(tx, dict) else 
            tx for tx in block_data.get("transactions", [])
        ]
        return cls(miner_numeric_id = block_data["miner_numeric_id"],
                miner_node_name = block_data["miner_node_name"],
                timestamp = block_data["timestamp"], 
                merkle_root = block_data["merkle_root"],
                nonce = block_data["nonce"],
                nbits = block_data["nbits"],
                transactions = transactions,
                )

    def to_dict(self):
        """
        Convert the block object into a dictionary for JSON serialization.
        """
        return {
                "miner_numeric_id":self.miner_numeric_id,
                "miner_node_name":self.miner_node_name,
                "timestamp":self.timestamp,
                "merkle_root":self.merkle_root,
                "nonce":self.nonce,
                "nbits":self.nbits,
                "transactions":
                    [tx.to_dict() if hasattr(tx, "to_dict") 
                     else tx for tx in self.transactions],
                }
  
    def compute_hash(self):
        """
        Compute the hash of the block.
        """
        block_content = {
                "miner_numeric_id":self.miner_numeric_id,
                "miner_node_name":self.miner_node_name,
                "timestamp":self.timestamp,
                "merkle_root":self.merkle_root,
                "nonce":self.nonce,
                "nbits":self.nbits,
            }
        
        encoded_block_string = json.dumps(block_content, sort_keys=True).encode()
        block_hash = hashlib.sha256(encoded_block_string).hexdigest()
        return block_hash