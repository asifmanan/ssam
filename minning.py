from flask import Flask, jsonify
from blockchain import Blockchain

#Part 2 - Minning the Blockchain
# Creating a webapp
app = Flask(__name__)

# Creating a Blockchain
blockchain = Blockchain()

# Minning a new block 
@app.route("/mine_block", methods = ['GET'])
def mine_block():
  previous_block = blockchain.get_previous_block()
  previous_proof = previous_block['proof']
  proof = blockchain.proof_of_work(previous_proof)
  previous_hash = blockchain.hash(previous_block)
  block = blockchain.create_block(proof, previous_hash)
  response = {
              'message': 'Congragulations! A new block was created',
              'index': block['index'], 
              'timestamp': block['timestamp'], 
              'proof': block['proof'], 
              'previous_hash': block['previous_hash'] 
              }
  return jsonify(response), 200


# Getting the full blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
  response = {
              'chain' : blockchain.chain, 
              'length' : len(blockchain.chain)
              }
  return jsonify(response), 200
  
# Checking is the blockchain is valid
@app.route("/is_valid", methods = ['GET'])
def is_valid():
  is_valid = blockchain.is_chain_valid(blockchain.chain)
  if is_valid:
    response = {"message":"The blockchain is valid"}
  else:
    response = {"message":"Oops! The blockchain is not valid"}
  return jsonify(response), 200

# Running the app 
app.run(host='0.0.0.0', port = 5000)