import logging
from blockchain.proof_of_work import ProofOfWork

class Miner:
  def __init__(self):
    """
    Initialize the miner.
    """
    self.pow = ProofOfWork()
  
  def mine_block(self, block_data):
    """
    Mines a new block with the given transaction root.
    """
    # Get the target from (difficulty) nbits
    golden_nonce = self.pow.find_valid_nonce(block_data)
    if golden_nonce is None:
      logging.warning("Failed to find a valid nonce for the block.")
      return None

    block_data.nonce = golden_nonce

    return block_data