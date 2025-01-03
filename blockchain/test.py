# from blockchain.proof_of_work import ProofOfWork

# nbits = ProofOfWork.target_to_nbits(int("00000ffff0000000000000000000000000000000000000000000000000000000",16))
# print(nbits)

# target = ProofOfWork.nbits_to_target(nbits)
# target = f"{target:064x}"
# print(f"Target: 0x{target}")

from blockchain.shard_staker import ShardStaker
from blockchain.blockchain import Blockchain

from transaction.transaction_manager import TransactionManager
from transaction.transaction import Transaction
from blockchain.shard_miner import ShardMiner
import json

tx_pool_file_path = "transaction/transaction_pool.json"
try:
    with open(tx_pool_file_path, 'r') as f:
        data = json.load(f)
        tx_pool = [Transaction(**tx) for tx in data]
except FileNotFoundError:
  print("File not found")


transaction_manager = TransactionManager(tx_pool,num_miners=2)
blockchain = Blockchain(transaction_manager)


gen_hash = blockchain.get_last_block().compute_hash()
print(f"Genesis Hash: {gen_hash}")

shard_miner = ShardMiner(miner_id=1, num_miners=3, transactions=tx_pool)
shard_block = shard_miner.create_shard_block()
print(f"Shard Block: {shard_block.compute_hash()}")


# print(shard_miner.alocd_transactions)

# print(f"Miner Transactions: {miner_tx}")

# shard_mt = shard_miner.process_transactions()
# print(f"Merkle Root: {shard_mt}")

# txs = transaction_manager.get_transactions_for_miner(1)
# print(f"transactions: {txs}")