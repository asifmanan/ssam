import time
from typing import List
from transaction.transaction_manager import TransactionManager
from transaction.transaction import Transaction
from blockchain.shard_block import ShardBlock
from blockchain.proof_of_work import ProofOfWork

class ShardMiner:
    def __init__(self, miner_id: int, num_miners: int, transactions: List[Transaction]):
        """
        Initializes the Shard Miner with its ID and access to the Transaction Manager.
        :param miner_id: ID of the miner.
        :param num_miners: Number of miners.
        :param transactions: List of transactions.
        """
        self.miner_id = miner_id
        self.transaction_manager = TransactionManager(num_miners=num_miners, transactions=transactions)
        self.pow = ProofOfWork()
        self.alocd_transactions = self.transaction_manager.get_transactions_for_miner(self.miner_id)

    def process_transactions(self):
        """
        Processes the assigned transactions, calculates the Merkle root, and timestamps it.
        :return: A merkle root of verified transactions.
        """
        # Transaction varification logic will be added here

        # Calculate the Merkle root
        merkle_root = self.transaction_manager.get_miner_merkle_root(self.miner_id)

        return merkle_root

    def mine_shard_block(self):
        """
        Creates a new block with the processed result.
        :return: A new shard block.
        """
        transactions = self.alocd_transactions
        merkle_root = self.process_transactions()
        timestamp = time.time()

        shard_block = ShardBlock(miner_id=self.miner_id, merkle_root=merkle_root, timestamp=timestamp, transactions=transactions)
        golden_nonce = self.get_golden_nonce(shard_block)
        shard_block.nonce = golden_nonce
        return shard_block
    
    def get_golden_nonce(self, shard_block: ShardBlock):
        """
        Mines a new block with the given transaction root.
        :param shard_block: The shard block to be mined.
        """
        golden_nonce = self.pow.find_valid_nonce(shard_block)
        return golden_nonce
    

    