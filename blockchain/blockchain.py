<<<<<<< HEAD:blockchain.py
# Blockchain Class

# Requirements
# 1. Flask 
# 2. Postman for testing 
# 3. Requests==2.32.3
=======
>>>>>>> modularization:blockchain/blockchain.py

import datetime
import hashlib
import json
from urllib.parse import urlparse
<<<<<<< HEAD:blockchain.py
from transactions import Transactions
=======
from blockchain.transactions import Transactions
from blockchain.block import Block
>>>>>>> modularization:blockchain/blockchain.py
import requests

# Blockchain Class 
class Blockchain:
  def __init__(self):
    self.chain = []
    self.transactions = Transactions()
    self._create_genesis_block()
    self.nodes = set()

  def _create_genesis_block(self):
    """
      Creates a genesis block
    """
    if len(self.chain) == 0:
      genesis_block = Block(index=0, 
                            timestamp=str(datetime.datetime.now()), 
                            proof=1,
                            previous_hash="0",
                            transactions=[]
                            )
      # block_hash = genesis_block.hash
      self.chain.append(genesis_block)

  def create_block(self, proof, previous_hash):
    """
      Creates a normal block
    """
    previous_block = self.get_last_block()
    new_block = Block(index = len(self.chain) + 1,
                      timestamp=str(datetime.datetime.now()),
                      proof=proof,
                      previous_hash=previous_block.hash,
                      transactions=self.transactions.get_transactions()
                      )

    self.chain.append(new_block)
    self.transactions.clear_transactions()
    return new_block
  
  # Returns the last block in the chain
  def get_last_block(self):
    """
      Returns the last block in the chain
    """
    return self.chain[-1]  

  def proof_of_work(self, previous_proof):
    new_proof = 1
    check_proof = False
    while check_proof is False:
      hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
      if hash_operation[:4] == '0000':
        check_proof = True
      else:
        new_proof +=1
    return new_proof
  
  # For blockchain validation 
  def hash(self, block):
    encoded_block = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(encoded_block).hexdigest()
  
  def get_block_by_index(self, index):
    return self.chain[index]
  
  def is_chain_valid(self, chain):
    previous_block = chain[0]
    block_index = 1
    while block_index < len(chain):
      block = chain[block_index]
      if block.previous_hash != previous_block.hash:
        return False
      previous_proof = previous_block.proof
      proof = block.proof
      hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
      if hash_operation[:4] != '0000':
        return False
      previous_block = chain[block_index]
      block_index += 1
    return True
  
  def record_transactions(self, sender, receiver, amount):
    self.transactions.add_transaction(sender, receiver, amount)
    # previous_block = Block.from_block(self.get_last_block())
    previous_block = self.get_last_block()
    return previous_block.index
  
  def add_node(self, address):
    parsed_url = urlparse(address)
    self.nodes.add(parsed_url.netloc)

  def replace_chain(self):
    network = self.nodes
    longest_chain = None
    max_length = len(self.chain)
    for node in network:
      response = requests.get(f'http://{node}/get_chain')
      if response.status_code == 200:
        new_length = response.json()['length']
        new_chain = response.json()['chain']
        if new_length > max_length and self.is_chain_valid(new_chain):
          max_length = new_length
          longest_chain = new_chain
    if longest_chain: 
      self.chain = longest_chain
      return True
    return False
