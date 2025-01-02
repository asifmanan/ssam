import time
from blockchain.main_block import MainBlock
from transaction.transaction_manager import TransactionManager
from transaction.utils import load_genesis_transactions
# Blockchain Class 
class Blockchain:
  def __init__(self, transaction_manager: TransactionManager):
    self.chain = []
    self.block_lookup_table = {}
    self.create_genesis_block()
    self.transaction_manager = transaction_manager

  def create_genesis_block(self):
    """
    Creates the genesis block of the blockchain.
    """
    genesis_block = MainBlock(
      index = 0,
      timestamp = str(1734129936.8752465),
      previous_hash = "0",
      tx_root = "1011a88e4e9231ad320625b235a22997ba68d99db47a808dcc059c07395082eb",
      staker_signature = "0x0",
      nbits = "0x1e0ffff0",
      nonce = 311285,
      transactions = load_genesis_transactions()
    )
    self.add_block(genesis_block)

  def create_block(self, staker_signature, tx_root, nonce: int=0, nbits=None, transactions: list=[]):
    """
    Creates a new block with the given transaction root.
    """
    previous_block = self.get_last_block()
    previous_hash = previous_block.compute_hash()
    
    new_block = MainBlock(
      index=len(self.chain),
      timestamp = str(time.time()),
      previous_hash = previous_hash,
      tx_root = tx_root,
      staker_signature = staker_signature,
      nbits = nbits,
      nonce = nonce,
      transactions = transactions
    )
    return new_block
  
  def add_block(self, block):
    """
    Add a block to the blockchain after validation.
    """
    if not self.is_block_valid(block):
      return False
    self.chain.append(block)
    self.block_lookup_table[block.compute_hash()] = block
    return True
  
  def get_last_block(self):
    """
    Returns the last block in the chain
    """
    return self.chain[-1]
  
  def get_previous_block(self, block):
    """
    Returns the previous block in the chain based on the hash of previous block.
    Params:
        block (Block): The Block object who's predecessor is required.

    Returns:
        Block: The previous block in the chain, or None if the block is the genesis block.
    """
    previous_hash = block.previous_hash
    if previous_hash == "0":
      return None
    return self.block_lookup_table.get(previous_hash, None)
  
  def is_block_valid(self, block):
    """
    Validates the block by checking its proof of work and previous.
    """
    # Genesis block validation
    if block.index == 0:
      return (block.previous_hash == "0" and 
              block.compute_hash() == "ed5fa58270a35492486115de286d6f8f7181654654091e49d311b15bbf2e0eec")
    
    # Other block validation
    previous_block = self.get_previous_block(block)
    if previous_block is None:
      return False

    # Validate previous hash
    if block.previous_hash != previous_block.compute_hash():
      return False
    
    return True
  
  def is_chain_valid(self):
    """
    Validates the entire blockchain.
    """
    # Validate the genesis block explicitly
    genesis_block = self.chain[0]
    if not self.is_block_valid(genesis_block):
        print("Genesis block validation failed.")
        return False

    # Validate the rest of the chain
    for i in range(1, len(self.chain)):
        if not self.is_block_valid(self.chain[i]):
            return False
    return True

  def replace_chain(self):
    pass
