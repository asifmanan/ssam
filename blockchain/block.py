import json
import hashlib
import datetime

class Block:
  def __init__(self, index, timestamp, transactions, proof, previous_hash):
    """
      Initialize a new block.
    """
    self.__index = index
    self.__timestamp = timestamp
    self.__transactions = transactions
    self.__proof = proof
    self.__previous_hash = previous_hash

  @classmethod
  def from_dict(cls, block_data):
    """
      Convert JSON Data into an instance of a Block class.
    """
    return cls(index = block_data["index"],
               timestamp = block_data["timestamp"], 
               transactions = block_data["transactions"], 
               proof = block_data["proof"], 
               previous_hash = block_data["previous_hash"])

  def to_dict(self):
    """
      Convert the block object into a dictionary for JSON serialization.
    """
    return {
            "index":self.index,
            "timestamp":self.timestamp,
            "transactions":self.transactions,
            "proof":self.proof,
            "previous_hash":self.previous_hash,
            "block_hash":self.hash
            }
  
  def _compute_hash(self):
    """
      Compute the hash of the block based on its content.
    """
    encoded_block_string = json.dumps(self.__dict__, sort_keys=True).encode()
    block_hash = hashlib.sha256(encoded_block_string).hexdigest()
    return block_hash
  
  @property
  def index(self):
    return self.__index
  
  @property
  def timestamp(self):
    return self.__timestamp
  
  @property 
  def proof(self):
    return self.__proof
  
  @property
  def previous_hash(self):
    return self.__previous_hash
  
  @property
  def transactions(self):
    return self.__transactions
  
  @property
  def hash(self):
    return self._compute_hash()