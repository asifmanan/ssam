from blockchain.proof_of_work import ProofOfWork

# nbits = ProofOfWork.target_to_nbits(int("0000ffff00000000000000000000000000000000000000000000000000000000",16))
# print(nbits)

# target = ProofOfWork.nbits_to_target(nbits)
# target = f"{target:064x}"
# print(f"Target: 0x{target}")

# Test nbits to target conversion
# nbits = "0x1f00ffff"
# new_target = ProofOfWork.nbits_to_target(nbits)
# new_target = f"{new_target:064x}"
# print(f"New Target: 0x{new_target}")

from blockchain.blockchain import Blockchain

blockchain = Blockchain()
# print(blockchain.chain)
genesis_block = blockchain.create_genesis_block()
added = blockchain.add_block(genesis_block)
print(added)
print(f"Genesis Block Hash: {genesis_block.compute_hash()}")

# pow = ProofOfWork(nbits="0x1e0ffff0")
# golden_nonce = pow.find_valid_nonce(genesis_block)
# print(f"Golden Nonce: {golden_nonce}")
# print(f"Genesis Block Hash: {genesis_block.compute_hash()}")
