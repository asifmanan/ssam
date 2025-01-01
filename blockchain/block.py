import json
import hashlib
from transaction.transaction_manager import TransactionManager
from transaction.transaction import Transaction

class Block:
  def __init__(self, index, timestamp, tx_root, previous_hash, nbits, nonce, transactions=[]):
    """
    Initialize a new block.
    """
    self.index = index
    self.timestamp = timestamp
    self.previous_hash = previous_hash
    self.tx_root = tx_root
    self.nbits = nbits
    self.nonce = nonce
    self.transactions = transactions

  @classmethod
  def from_dict(cls, block_data):
    """
    Convert JSON Data into an instance of a Block class.
    """
    transactions = [
        Transaction.from_dict(tx) if isinstance(tx, dict) else tx
        for tx in block_data.get("transactions", [])
    ]
    return cls(index = block_data["index"],
               timestamp = block_data["timestamp"], 
               previous_hash = block_data["previous_hash"],
               tx_root = block_data["tx_root"], 
               nbits = block_data["nbits"],
               nonce = block_data["nonce"],
               transactions = transactions,
               )

  def to_dict(self):
    """
    Convert the block object into a dictionary for JSON serialization.
    """
    return {
            "index":self.index,
            "timestamp":self.timestamp,
            "previous_hash":self.previous_hash,
            "tx_root":self.tx_root,
            "nbits":self.nbits,
            "nonce":self.nonce,
            "transactions":[tx.to_dict() if hasattr(tx, "to_dict") else tx for tx in self.transactions],
            }
  
  def compute_hash(self):
    """
    Compute the hash of the block.
    """
    block_content = {
      "index":self.index,
      "timestamp":self.timestamp,
      "previous_hash":self.previous_hash,
      "tx_root":self.tx_root,
      "nbits":self.nbits,
      "nonce":self.nonce,
    }
    
    encoded_block_string = json.dumps(block_content, sort_keys=True).encode()
    block_hash = hashlib.sha256(encoded_block_string).hexdigest()
    return block_hash