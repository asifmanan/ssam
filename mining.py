# Reference
class Mining:
  def __init__(self, blockchain, node_address, owner_id):
    self.blockchain = blockchain
    self.node_address = node_address
    self.owner_id = owner_id
  def mine_block(self):
    previous_block = self.blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = self.blockchain.proof_of_work(previous_proof)
    previous_hash = self.blockchain.hash(previous_block)
    self.blockchain.record_transactions(sender=self.node_address, receiver=self.owner_id,amount=10)
    block = self.blockchain.create_block(proof, previous_hash)
    response = {
                'message': 'Congragulations! A new block was created',
                'index': block['index'], 
                'timestamp': block['timestamp'], 
                'proof': block['proof'], 
                'previous_hash': block['previous_hash'] , 
                'transactions': block['transactions']
                }
    return response
