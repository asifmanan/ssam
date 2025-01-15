import time
import json
import logging
import os
from blockchain.main_block import MainBlock
from transaction.utils import load_genesis_transactions
# Blockchain Class 
class Blockchain:
  def __init__(self):
    """
    Initializes the blockchain with the genesis block.
    """
    self.chain = []
    self.block_lookup_table = {}
    self.create_genesis_block()
    

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
      nonce = 820329,
      shard_data = {},
      transactions = load_genesis_transactions()
    )
    
    self.add_block(genesis_block)
    

  def create_block(self, staker_signature, tx_root, nonce: int=0, nbits=None, shard_data: dict=None,transactions: list=[]):
    """
    Creates a new block with the given transaction root.
    :param staker_signature: The signature of the staker.
    :param tx_root: The Merkle root of the transactions.
    :param nonce: The nonce value for the block (for backward compatability).
    :param nbits: The target difficulty for the block. (for backward compatability).
    :param transactions: List of transactions to be included in the block.
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
      shard_data = shard_data if shard_data is not None else {},
      transactions = transactions
    )
    return new_block
  
  def add_block(self, block):
    """
    Add a block to the blockchain after validation.
    :param block: The block to be added.
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
    :Params: block (Block): The Block object who's predecessor is required.

    :Returns: Block: The previous block in the chain, or None if the block is the genesis block.
    """
    previous_hash = block.previous_hash
    if previous_hash == "0":
      return None
    return self.block_lookup_table.get(previous_hash, None)
  
  def is_block_valid(self, block):
    """
    Validates the block by checking its proof of work and previous.

    :param block: The block to be validated.
    """
    # Genesis block validation
    if block.index == 0:
      return (block.previous_hash == "0" and 
              block.compute_hash() == "00000110b03f6bca0513e614094a7d3b42729bacc65d6ae99b7088f5eebe0f28")
    
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

  def replace_chain(self, new_chain):
    """
    Replaces the current chain with a new chain if the new chain is valid.
    :param new_chain: The new chain to replace the current chain with.
    """
    if len(new_chain) <= len(self.chain):
      return False
    if not self.is_chain_valid():
      return False
    self.chain = new_chain
    self.block_lookup_table = {block.compute_hash(): block for block in new_chain}
    return True
  
  def write_to_json(self, node_name, block, file_path=None):
      """
      Append a new block to the blockchain JSON file in the shared docker volume.

      :param node_name: The name of the staker node.
      :param block: The new block to append.
      :param file_path: Optional custom file path. If not provided, the filename will be based on the node name.
      """
      try:
          # Default filename in the shared volume directory
          if not file_path:
              file_path = f"/app/data/{node_name}_blockchain.json"

          # Check if the file exists and is not empty
          if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
              # Reading the existing blockchain
              try:
                  with open(file_path, "r") as json_file:
                      blockchain_data = json.load(json_file)
              except json.JSONDecodeError:
                  logging.warning(f"File {file_path} is corrupted. Reinitializing.")
                  blockchain_data = []
          else:
              # Initialize a new blockchain file if it does not exist or is empty
              blockchain_data = []

          # Add the new block
          blockchain_data.append(block.to_dict())

          # Write back to the JSON file
          with open(file_path, "w") as json_file:
              json.dump(blockchain_data, json_file, indent=4)

          # logging.info(f"Block {block.index} added to {file_path}.")
      except Exception as e:
          logging.error(f"Failed to append block to {file_path}: {e}")
