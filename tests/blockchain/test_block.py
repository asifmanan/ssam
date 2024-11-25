import pytest
import datetime
from blockchain.block import Block


def test_block_initialization():
    current_time = str(datetime.datetime.now())
    block = Block(index=1, 
                  timestamp=current_time, 
                  transactions=[{"sender": "A", "receiver": "B", "amount": 10}], 
                  proof=100, 
                  previous_hash="abcd1234")
    assert block.index == 1
    assert block.timestamp == current_time
    assert block.transactions == [{"sender": "A", "receiver": "B", "amount": 10}]
    assert block.proof == 100
    assert block.previous_hash == "abcd1234"

def test_block_to_dict():
    current_time = str(datetime.datetime.now())
    block = Block(index=1, 
                  timestamp = current_time, 
                  transactions=[{"sender": "A", "receiver": "B", "amount": 10}], 
                  proof=100, 
                  previous_hash="abcd1234")
    block_dict = block.to_dict()
    assert block_dict["index"] == 1
    assert block_dict["timestamp"] == current_time
    assert block_dict["transactions"] == [{"sender": "A", "receiver": "B", "amount": 10}]
    assert block_dict["proof"] == 100
    assert block_dict["previous_hash"] == "abcd1234"
    assert "block_hash" in block_dict

def test_block_hash_computation():
    block = Block(index=1, 
                  timestamp=str(datetime.datetime.now()), 
                  transactions=[{"sender": "A", "receiver": "B", "amount": 10}], 
                  proof=100, 
                  previous_hash="abcd1234")
    block_hash = block.hash
    assert isinstance(block_hash, str)
    assert len(block_hash) == 64  # SHA-256 hash length
