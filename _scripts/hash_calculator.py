import json
import hashlib

# Load the blockchain data from the JSON file
with open("./data/staker10_blockchain.json", "r") as file:
    blockchain = json.load(file)

def calculate_block_hash(block):
    """
    Calculate the SHA-256 hash of a block.
    """
    # Exclude the block_hash field if present
    # block_copy = {key: value for key, value in block.items() if key != "block_hash"}
    block_copy = {key: value for key, value in block.items() if key not in ["block_hash", "transactions"]}
    # Convert the block to a JSON string and encode it to bytes
    block_string = json.dumps(block_copy, sort_keys=True).encode()
    
    # Compute the hash
    return hashlib.sha256(block_string).hexdigest()

# Iterate through the blockchain and calculate the hash for each block
for block in blockchain:
    block_index = block["index"]
    block_hash = calculate_block_hash(block)
    print(f"Index: {block_index}, Hash: {block_hash}")