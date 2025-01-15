from blockchain.blockchain import Blockchain
from blockchain.proof_of_work import ProofOfWork
from blockchain.miner import Miner
import logging

# Initialize components
blockchain = Blockchain()
proof_of_work = ProofOfWork()
miner = Miner()

# Print the block information
def print_block(block):
    print(f"New block added! Index: {block.index}")
    print(f"Hash: {block.compute_hash()}")
    print(f"Previous Hash: {block.previous_hash}")
    print(f"Nonce: {block.nonce}")
    print(f"Timestamp: {block.timestamp}")
    print(f"Tx Root: {block.tx_root}")
    print(f"nbits: {block.nbits}")
    print(f"Target: {proof_of_work.get_current_target():064x}")
    print(f"Transactions: ")
    for tx in block.transactions:
        print(f"  Sender: {tx.sender}, Receiver: {tx.recipient}, Amount: {tx.amount}, Signature: {tx.signature}")

    print(f"-{'-'*10}-")



for i in range(3):
    # Mine a new block
    block = blockchain.create_block(staker_signature="staker123", tx_root="0x0")
    block.nbits = proof_of_work.target_to_nbits(proof_of_work.get_current_target())
    mined_block = miner.mine_block(block)
    added = blockchain.add_block(mined_block)
    print(f"Block added: {added}")

    if mined_block:
        print_block(mined_block)
    else:
        logging.warning("Failed to mine the block.")