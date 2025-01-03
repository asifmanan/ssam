import json
import hashlib
from transaction.transaction_manager import TransactionManager
from transaction.transaction import Transaction

class MainBlock:
  def __init__(self, index, timestamp, tx_root, previous_hash, staker_signature, nbits, nonce=0, transactions=[]):
    """
    Initialize a new block.
    :param index: The index of the block.
    :param timestamp: The timestamp of the block.
    :param tx_root: The Merkle root of the transactions.
    :param previous_hash: The hash of the previous block.
    :param staker_signature: The signature of the staker.
    :param nbits: The target difficulty for the block. (for compatability with PoW Systems).
    :param nonce: The nonce value for the block (for compatability with PoW Sytems).
    :param transactions: List of transactions in the block.
    """
    self.index = index
    self.timestamp = timestamp
    self.previous_hash = previous_hash
    self.tx_root = tx_root
    self.staker_signature = staker_signature
    self.nbits = nbits
    self.nonce = nonce
    self.transactions = transactions

  @classmethod
  def from_dict(cls, block_data):
    """
    Convert JSON Data into an instance of a Block class.
    :param block_data: The JSON data to be converted into a block.
    """
    transactions = [
        Transaction.from_dict(tx) if isinstance(tx, dict) else tx
        for tx in block_data.get("transactions", [])
    ]
    return cls(index = block_data["index"],
               timestamp = block_data["timestamp"], 
               previous_hash = block_data["previous_hash"],
               tx_root = block_data["tx_root"], 
               staker_signature = block_data["staker_signature"],
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
            "staker_signature":self.staker_signature,
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
      "staker_signature":self.staker_signature,
      "nbits":self.nbits,
      "nonce":self.nonce,
    }
    
    encoded_block_string = json.dumps(block_content, sort_keys=True).encode()
    block_hash = hashlib.sha256(encoded_block_string).hexdigest()
    return block_hash