from blockchain.proof_of_work import ProofOfWork

# nbits = ProofOfWork.target_to_nbits(int("0000ffff00000000000000000000000000000000000000000000000000000000",16))
# print(nbits)

# target = ProofOfWork.nbits_to_target(nbits)
# target = f"{target:064x}"
# print(f"Target: 0x{target}")

nbits = "0x1f00ffff"
new_target = ProofOfWork.nbits_to_target(nbits)
new_target = f"{new_target:064x}"
print(f"New Target: 0x{new_target}")



