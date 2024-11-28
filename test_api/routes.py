"""
This Flask API serves as a testing interface for the blockchain project.
It is not intended for production use and focuses on exposing basic blockchain functionality. 
"""

from flask import Flask, jsonify, request
from blockchain.blockchain import Blockchain
from uuid import uuid4

from blockchain.block import Block

#Part 2 - Minning the Blockchain

# Creating an address for the node 
node_address = str(uuid4()).replace('-','')
owner_id = "test_api"


# Creating a webapp
app = Flask(__name__)

# Creating a Blockchain
blockchain = Blockchain()

# Minning a new block 
@app.route("/mine_block", methods = ['GET'])
def mine_block():
  """
    Mines a new block, simulating the mining process and adding a reward transaction.
  """
  previous_block = blockchain.get_last_block()
  previous_proof = previous_block.proof
  proof = blockchain.proof_of_work(previous_proof)
  previous_hash = previous_block.hash
  blockchain.record_transactions(sender=node_address, receiver=owner_id,amount=10)
  block = blockchain.create_block(proof, previous_hash)
  response = {
              'message': 'New block created',
              'index': block.index, 
              'timestamp': block.timestamp, 
              'proof': block.proof, 
              'previous_hash': block.previous_hash , 
              'transactions': block.transactions
              }
  return jsonify(response), 200


# Getting the full blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
  """
    Retrieves the entire blockchain.
  """
  response = {
              'chain' : [block.to_dict() for block in blockchain.chain], 
              'length' : len(blockchain.chain)
              }
  return jsonify(response), 200
  
# Checking is the blockchain is valid
@app.route("/is_valid", methods = ['GET'])
def is_valid():
  """
    Validates the current blockchain.
  """
  is_valid = blockchain.is_chain_valid(blockchain.chain)
  if is_valid:
    response = {"message":"The blockchain is valid"}
  else:
    response = {"message":"Oops! The blockchain is not valid"}
  return jsonify(response), 200

# Adding a new transaction to the blockchain 
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
  json = request.get_json()
  transaction_keys = ['sender', 'receiver', 'amount']
  if not all (key in json for key in transaction_keys):
    return "Missing Parameters in transaction", 400
  index = blockchain.record_transactions(json['sender'], json['receiver'], json['amount'])
  response = {'message': f'This transaction will be added to block {index}'}
  return jsonify(response), 201

# Connecting new Nodes 
@app.route('/connect_node', methods = ['POST'])
def connect_node():
  json = request.get_json()
  nodes = json.get('nodes')
  if nodes is None:
    return "No node", 400
  for node in nodes:
    blockchain.add_node(node)
  response = {"message":"All the nodes are now connected, the blockchain now contains the following nodes",
              "total_nodes": list(blockchain.nodes)}
  return jsonify(response), 201

# Replacing the chain
@app.route("/replace_chain", methods = ['GET'])
def replace_chain():
  is_chain_replaced = blockchain.replace_chain()
  if is_chain_replaced:
    response = {"message":"The chain was replaced",
                "chain":blockchain.chain}
  else:
    response = {"message":"The current node is running the longest chain in the network, chain not replaced",
                "chain":blockchain.chain}
  return jsonify(response), 200

# Running the app 
if __name__ == "__main__":
  app.run(host='0.0.0.0', port = 5000)