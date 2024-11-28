
class Mining:
  def __init__(self, blockchain, node_address, owner_id):
    """
      Initialize the Mining instance with a blockchain, node address, and owner ID.
    """
    self.blockchain = blockchain
    self.node_address = node_address
    self.owner_id = owner_id

  def mine_block(self):
    """
      Mines a new block and adds it to the local blockchain.
    """
    try:
      # Get the last block from the block chain. 
      last_block = self.blockchain.get_last_block()
      last_proof = last_block.proof

      # Perform proof of work
      proof = self.blockchain.proof_of_work(last_proof)

      # Record the reward transaction
      self.blockchain.record_transactions(
        sender=self.node_address, receiver=self.owner_id,amount=10
        )
      
      # Create a new block 
      block = self.blockchain.create_block(proof, last_block.hash)
      print("New Block Mined, Block Index = " + block.index)

      # Returning a structured message 
      response = {
                  'message': 'A new block was created',
                  'index': block.index, 
                  'timestamp': block.timestamp, 
                  'proof': block.proof, 
                  'previous_hash': block.previous_hash , 
                  'transactions': block.transactions
                  }
    except Exception as e:
      response = {
                  'message': f'An error occured while mining the block: {e}',
                  'index': None
                  }
    return block
