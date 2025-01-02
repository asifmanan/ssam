import time
from typing import List
from transaction.transaction_manager import TransactionManager
from transaction.transaction import Transaction
from blockchain.shard_block import ShardBlock

class ShardMiner:
    def __init__(self, miner_id: int, num_miners: int, transactions: List[Transaction]):
        """
        Initializes the Shard Miner with its ID and access to the Transaction Manager.
        :param miner_id: ID of the miner.
        :param num_miners: Number of miners.
        :param transactions: List of transactions.
        """
        self.miner_id = miner_id
        self.transaction_manager = TransactionManager(num_miners, miner_id=miner_id, transactions=transactions)
        self.alocd_transactions = self.transaction_manager.get_transactions_for_miner(self.miner_id)

    def process_transactions(self):
        """
        Processes the assigned transactions, calculates the Merkle root, and timestamps it.
        :return: A merkle root of verified transactions.
        """
        # Transaction varification logic will be added here

        # Calculate the Merkle root
        merkle_root = self.transaction_manager.calculate_merkle_root_for_miner(self.miner_id)

        return merkle_root

    def create_shard_block(self):
        """
        Creates a new block with the processed result.
        :return: A new shard block.
        """
        transactions = self.alocd_transactions
        merkle_root = self.process_transactions()
        timestamp = time.time()

        shard_block = ShardBlock(miner_id=self.miner_id, merkle_root=merkle_root, timestamp=timestamp, transactions=transactions)

        return shard_block
    
    def send_to_staker(self, staker_node):
        """
        Sends the processed result to the Staker Node.
        :param staker_node: Instance of the Staker Node.
        """
        result = self.process_transactions()
        staker_node.receive_merkle_root(result)