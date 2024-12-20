import hashlib
import json
from typing import List
from transaction.transaction import Transaction

class TransactionManager:
    def __init__(self, tx_list=None):
        if tx_list:
            self.tx_pool = tx_list
        else:
            self.tx_pool = self.load_transactions()

    def load_transactions(self, tx_pool_file_path=None):
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
    
    
    def calculate_merkle_root(self):
        """
        Calculate the Merkle root of the transactions.
        :return: Hexadecimal Merkle root string.
        """
        if not self.tx_pool:
            return None

        # Helper function to hash two nodes
        def hash_pair(hash1, hash2):
            return hashlib.sha256((hash1 + hash2).encode('utf-8')).hexdigest()

        # Get the hashes of all transactions
        tx_hashes = [tx.calculate_hash() for tx in self.tx_pool]

        # Build the Merkle tree
        while len(tx_hashes) > 1:
            # If odd number of hashes, duplicate the last hash
            if len(tx_hashes) % 2 == 1:
                tx_hashes.append(tx_hashes[-1])

            # Pairwise hash to get the next level
            tx_hashes = [hash_pair(tx_hashes[i], tx_hashes[i + 1]) for i in range(0, len(tx_hashes), 2)]

        # The final hash is the Merkle root
        return tx_hashes[0]