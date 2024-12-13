from blockchain.blockchain import Blockchain
from blockchain.proof_of_work import ProofOfWork
from blockchain.miner import Miner
import logging

# Initialize components
blockchain = Blockchain()
proof_of_work = ProofOfWork()
miner = Miner(blockchain, proof_of_work)

# Mine a new block with a sample transaction root
tx_root = "0x1234567890abcdef"
mined_block = miner.mine_block(tx_root=tx_root)

if mined_block:
    print(f"New block added! Index: {mined_block.index}, Hash: {mined_block.compute_hash()}")
    print(f"Previous Hash: {mined_block.previous_hash}, Nonce: {mined_block.nonce}")
    print(f"Timestamp: {mined_block.timestamp}, Tx Root: {mined_block.tx_root}")
    print(f"Target: {proof_of_work.nbits_to_target(mined_block.nbits):064x}")
else:
    logging.warning("Failed to mine the block.")