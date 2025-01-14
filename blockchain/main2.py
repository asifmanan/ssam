from blockchain.shard_miner import ShardMiner
from transaction.transaction_manager import TransactionManager

transactions = TransactionManager.load_transactions()
node_name = "miner1"
num_miners = 2
shard_miner = ShardMiner(0, num_miners, transactions)

shard_block = shard_miner.mine_shard_block()

print(f"Shard Block: {shard_block.to_dict()}")