import hashlib
import json
from typing import List
from transaction.transaction import Transaction

class TransactionManager:
    def __init__(self, num_miners: int, miner_id, transactions: List[Transaction]):
        """
        Initializes the TransactionManager with miners and a pool of transactions.
        :param num_miners: Number of miners.
        :param transactions: List of transactions.
        """
        self.num_miners = num_miners
        self.transaction_pool = transactions
        self.miner_id = miner_id

    def get_transactions_for_miner(self, miner_id: int=None) -> List[Transaction]:
        """
        Returns the subset of transactions assigned to a specific miner.
        :param miner_id: ID of the miner.
        :return: List of transactions for the miner.
        """
        # Distribute transactions deterministically among miners
        if miner_id is None:
            miner_id = self.miner_id
        miner_transactions = [
            tx for i, tx in enumerate(self.transaction_pool) if i % self.num_miners == miner_id
        ]
        return miner_transactions
    
    def save_transactions(self, transactions: List[Transaction]):
        """
        Save transactions to the pool file.
        :param transactions: List of Transaction objects.
        """
        with open(self.tx_pool_file, 'w') as f:
            json.dump([tx.to_dict() for tx in transactions], f, indent=4)

    def add_transaction(self, transaction: Transaction):
        """
        Add a new transaction to the pool.
        :param transaction: Transaction object.
        """
        self.tx_pool.append(transaction)
        self.save_transactions(self.tx_pool)

    def remove_transactions(self, transactions_to_remove: List[Transaction]):
        """
        Remove transactions from the pool.
        :param transactions_to_remove: List of Transaction objects.
        """
        current_transactions = self.load_transactions()
        current_transactions = [
            tx for tx in current_transactions if tx.calculate_hash() not in
            {tx.calculate_hash() for tx in transactions_to_remove}
        ]
        self.save_transactions(current_transactions)

    def get_transactions(self):
        return self.tx_pool
    
    
    def calculate_merkle_root(self, miner_id: int=None) -> str:
        """
         Calculates the Merkle root for the subset of transactions processed by a specific miner.
        :param miner_id: ID of the miner.
        :return: Merkle root as a hex string.
        """
        if miner_id is None:
            transactions = self.transaction_pool
        else:
            transactions = self.get_transactions_for_miner(miner_id)
        if not transactions:
            return None

        # Helper function to hash two nodes
        def hash_pair(hash1, hash2):
            return hashlib.sha256((hash1 + hash2).encode('utf-8')).hexdigest()

        # Get the hashes of all transactions
        tx_hashes = [tx.calculate_hash() for tx in transactions]

        # Build the Merkle tree
        while len(tx_hashes) > 1:
            # If odd number of hashes, duplicate the last hash
            if len(tx_hashes) % 2 == 1:
                tx_hashes.append(tx_hashes[-1])

            # Pairwise hash to get the next level
            tx_hashes = [hash_pair(tx_hashes[i], tx_hashes[i + 1]) 
                         for i in range(0, len(tx_hashes), 2)
                         ]

        # The final hash is the Merkle root
        return tx_hashes[0]
    
    def clear_transaction_pool(self):
        """
        Clear the transaction pool.
        """
        self.tx_pool = []