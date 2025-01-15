from blockchain.proof_of_work import ProofOfWork

# nbits = ProofOfWork.target_to_nbits(int("0000ffff00000000000000000000000000000000000000000000000000000000",16))
# print(nbits)

# Test Target to nbits
# target = "00000ffff0000000000000000000000000000000000000000000000000000000"
# nbits = ProofOfWork.target_to_nbits(int(target,16))
# print(f"Target: 0x{nbits}")

# Test nbits to target conversion
# nbits = "0x1f00ffff"
# new_target = ProofOfWork.nbits_to_target(nbits)
# new_target = f"{new_target:064x}"
# print(f"New Target: 0x{new_target}")

# from blockchain.blockchain import Blockchain
# blockchain = Blockchain()
# genesis_block = blockchain.create_genesis_block()
# added = blockchain.add_block(genesis_block)
# print(added)
# print(f"Genesis Block Hash: {genesis_block.compute_hash()}")

# pow = ProofOfWork(nbits="0x1e0ffff0")
# golden_nonce = pow.find_valid_nonce(genesis_block)
# print(f"Golden Nonce: {golden_nonce}")
# print(f"Genesis Block Hash: {genesis_block.compute_hash()}")


# Test shardminer PoW
# nnbits = "0x1f00ffff"
# nnbits = "0x1e0ffff0"
# from transaction.transaction_manager import TransactionManager
# from blockchain.shard_miner import ShardMiner
# transactions = TransactionManager.load_transactions()
# shard_miner = ShardMiner(miner_numeric_id=0, miner_node_name="Miner0", num_miners=2, transactions=transactions, nbits=nnbits)
# shard_block = shard_miner.mine_shard_block()
# print(f"Shard Block Hash: {shard_block.compute_hash()}")
# print(f"Shard Block Nonce: {shard_block.nonce}")


# test get target from PoW

# For 4 Leading Zeros
# nbits1 = "0x1f00ffff"

# For 5 Leading Zeros
# nbits2 ="0x1e0ffff0"
pow = ProofOfWork(nbits="0x1e0ffff0")
print(f"Target in nbits: {pow.get_current_target_nbits()}")
print(f"Target in hex: {pow.get_current_target_hex()}")