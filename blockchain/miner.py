import logging

class Miner:
  def __init__(self, blockchain):
    """
    Initialize the miner with a reference to the blockchain and ProofOfWork.
    :param blockchain: The blockchain object.
    """
    self.blockchain = blockchain
    self.pow = self.blockchain.pow
  
  def mine_block(self):
    """
    Mines a new block with the given transaction root.
    """

    # Create a new block with the given parameters
    new_block = self.blockchain.create_block()
    
    # Get the target from (difficulty) nbits
    golden_nonce = self.pow.find_valid_nonce(new_block)
    if golden_nonce is None:
      logging.warning("Failed to find a valid nonce for the block.")
      return None

    new_block.nonce = golden_nonce

    # Add the mined block to the blockchain
    if self.blockchain.add_block(new_block):
      return new_block
    else:
      logging.warning("Failed to add the mined block to the blockchain.")
      return None