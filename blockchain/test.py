from blockchain.proof_of_work import ProofOfWork

nbits = ProofOfWork.target_to_nbits(int("00000ffff0000000000000000000000000000000000000000000000000000000",16))
print(nbits)

target = ProofOfWork.nbits_to_target(nbits)
target = f"{target:064x}"
print(f"Target: 0x{target}")