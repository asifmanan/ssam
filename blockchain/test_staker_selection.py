from blockchain.blockchain import Blockchain
from blockchain.shard_staker import ShardStaker
from transaction.transaction_manager import TransactionManager
from blockchain.main_block import MainBlock


class MockTransactionManager(TransactionManager):
    def __init__(self):
        # Dummy data for initialization
        super().__init__(transactions=[], num_miners=1)

    def calculate_merkle_root(self, transactions):
        # Dummy Merkle root calculation for testing
        return "mocked_merkle_root"

def simulate_staker_selection_rounds(rounds=4):
    # Initialize mock transaction manager
    transaction_manager = MockTransactionManager()

    # Initialize blockchain
    blockchain = Blockchain(transaction_manager)

    # Initialize ShardStaker
    shard_staker = ShardStaker(transaction_manager, blockchain)

    # Add stakers and stakes
    shard_staker.add_stake("staker1", 40)
    shard_staker.add_stake("staker2", 25)
    shard_staker.add_stake("staker3", 20)

    print("\n=== Staker Selection Simulation ===\n")

    # Simulate multiple rounds
    for round_number in range(1, rounds + 1):
        print(f"--- Round {round_number} ---")
        # Select a staker
        selected_staker = shard_staker.select_staker()
        print(f"Selected Staker: {selected_staker}")

        # Simulate block proposal
        new_block = blockchain.create_block(
            staker_signature=selected_staker,
            tx_root="mocked_merkle_root",
            transactions=[]
        )

        # Add the new block to the blockchain
        added = blockchain.add_block(new_block)
        if added:
            print(f"Block {new_block.index} added by {selected_staker}")
        else:
            print(f"Block {new_block.index} rejected (invalid)")

        print(f"Blockchain now has {len(blockchain.chain)} blocks.\n")

# Run the simulation
if __name__ == "__main__":
    simulate_staker_selection_rounds(rounds=10)