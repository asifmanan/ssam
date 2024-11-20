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
    return self.compute_hash()