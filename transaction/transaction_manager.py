import hashlib
import json
from typing import List
from transaction.transaction import Transaction

class TransactionManager:
    def __init__(self, transactions: List[Transaction], num_miners: int):
        """
        Initializes the TransactionManager with miners and a pool of transactions.
        :param num_miners: Number of miners.
        :param transactions: List of transactions.
        """
        
        self.num_miners = num_miners
        self.transaction_pool = transactions
        
    def get_num_miners(self):
        return self.num_miners
    
    def get_transactions(self):
        return self.transaction_pool
    
    def get_transactions_for_miner(self, miner_id: int=None) -> List[Transaction]:
        """
        Returns the subset of transactions assigned to a specific miner.
        :param miner_id: ID of the miner.
        :return: List of transactions for the miner.
        """
        # Distribute transactions deterministically among miners
        if miner_id is None:
            raise ValueError("Miner ID is required to get transactions for miners, otherwise use get_transactions() to get all the transactions from the pool.")
        
        miner_transactions = [
            tx for i, tx in enumerate(self.get_transactions()) if i % self.num_miners == miner_id
        ]

        # miner_transactions = []
        # transactions = self.get_transactions() 
        # print("miner id: " + str(miner_id)) 
        # print(f"num miners: {self.num_miners}")
        # # Retrieve all transactions
        # for i, tx in enumerate(transactions):
        #     print("i:" + str(i))
        #     rem = i % self.num_miners
        #     print(f"Remainder: {rem}")
        #     if rem == miner_id:
        #         print("appending")
        #         miner_transactions.append(tx)
        return miner_transactions

    
    def get_miner_merkle_root(self, miner_id: int) -> str:
        """
        Get the Merkle root for a specific miner.
        :param miner_id: ID of the miner.
        :return: Merkle root as a hex string.
        """
        miner_transactions = self.get_transactions_for_miner(miner_id)
        return self.calculate_merkle_root(miner_transactions)

    @classmethod
    def calculate_merkle_root(cls, transactions: List[Transaction]) -> str:
        """
        Calculates the Merkle root for the transactions in the list provided.
        :param transactions: List of Transaction objects.
        :return: Merkle root as a hex string.
        """
        if not transactions:
            return ""

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
    
    @classmethod
    def load_transactions(cls, tx_pool_file_path=None):
        """
        Load transactions from the pool file.
        :return: List of Transaction objects.
        """
        if not tx_pool_file_path:
            tx_pool_file_path = "transaction/transaction_pool.json"
        try:
            with open(tx_pool_file_path, 'r') as f:
                data = json.load(f)
                return [Transaction(**tx) for tx in data]
        except FileNotFoundError:
            return []
    
    def clear_transaction_pool(self):
        """
        Clear the transaction pool.
        """
        self.tx_pool = []