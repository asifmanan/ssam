import pytest
import hashlib
from blockchain.blockchain import Blockchain

def test_create_genesis_block():
    blockchain = Blockchain()
    assert len(blockchain.chain) == 1
    genesis_block = blockchain.chain[0]
    assert genesis_block.index == 0
    assert genesis_block.previous_hash == "0"

def test_create_block():
    blockchain = Blockchain()
    proof = 12345
    previous_hash = blockchain.chain[-1].hash
    new_block = blockchain.create_block(proof, previous_hash)
    assert len(blockchain.chain) == 2
    assert new_block.index == 2
    assert new_block.proof == proof
    assert new_block.previous_hash == previous_hash

def test_get_last_block():
    blockchain = Blockchain()
    last_block = blockchain.get_last_block()
    assert last_block.index == 0  # Genesis block initially

def test_proof_of_work():
    blockchain = Blockchain()
    previous_proof = blockchain.chain[-1].proof
    proof = blockchain.proof_of_work(previous_proof)
    hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
    assert hash_operation[:4] == "0000"

def test_is_chain_valid():
    blockchain = Blockchain()
    # Manually add a block
    proof = blockchain.proof_of_work(blockchain.chain[-1].proof)
    blockchain.create_block(proof, blockchain.chain[-1].hash)
    assert blockchain.is_chain_valid(blockchain.chain)

def test_record_transactions():
    blockchain = Blockchain()
    index = blockchain.record_transactions(sender="A", receiver="B", amount=100)
    assert index == blockchain.chain[-1].index

def test_add_node():
    blockchain = Blockchain()
    blockchain.add_node("http://127.0.0.1:5000")
    assert "127.0.0.1:5000" in blockchain.nodes
