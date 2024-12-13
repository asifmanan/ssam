import time
from blockchain.block import Block
from blockchain.proof_of_work import ProofOfWork

# Blockchain Class 
class Blockchain:
  def __init__(self):
    self.chain = []
    self.pow = ProofOfWork()

  def create_block(self, tx_root=None, nonce=0, nbits=None):
    """
    Creates a new block with the given transaction root.
    """
    if nbits is None:
      nbits = self.pow.target_to_nbits(self.pow.MAX_TARGET)
    
    if len(self.chain) == 0:
      previous_hash = "0"
    else:
      previous_block = self.get_previous_block()
      previous_hash = previous_block.compute_hash()
    
    new_block = Block(
      index=len(self.chain),
      timestamp = str(time.time()),
      previous_hash = previous_hash,
      tx_root = tx_root,
      nbits = nbits,
      nonce = nonce
    )
    return new_block
  
  def add_block(self, block):
    """
    Add a block to the blockchain after validation.
    """
    if not self.is_block_valid(block):
      return False
    self.chain.append(block)
    return True
  
  def get_previous_block(self):
    """
    Returns the last block in the chain
    """
    return self.chain[-1]
  
  def is_block_valid(self, block):
    """
    Validates the block by checking its proof of work and previous.
    """
    # validate proof of work
    target = self.pow.nbits_to_target(block.nbits)
    if not self.pow.is_valid_proof(block, target):
      return False
    
    # Validate previous hash
    if block.index != 0:
      # Skip genesis block validation of previous hash
      previous_block = self.get_previous_block()

      # Validate previous hash
      if block.previous_hash != previous_block.compute_hash():
        return False
    
    return True
  
  def is_chain_valid(self):
    """
    Validates the entire blockchain.
    """
    for i in range(1, len(self.chain)):
      current_block = self.chain[i]   

      # validate hash chain
      if not self.is_block_valid(current_block):
        return False
      
    return True   

  def replace_chain(self):
    pass
