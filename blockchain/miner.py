import logging
from blockchain.proof_of_work import ProofOfWork

class Miner:
  def __init__(self):
    """
    Initialize the miner.
    """
    self.pow = ProofOfWork()
  
  def mine_block(self, block):
    """
    Mines a new block with the given the block_data.
    """
    # Get the target from (difficulty) nbits
    golden_nonce = self.pow.find_valid_nonce(block)
    if golden_nonce is None:
      logging.warning("Failed to find a valid nonce for the block.")
      return None

    block.nonce = golden_nonce

    return block