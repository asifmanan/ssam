import time
from transaction.transaction import Transaction
from transaction.transaction_manager import TransactionManager


tx_manager = TransactionManager()
tx_pool = tx_manager.load_transactions()



# Calculate hash
# print("Transaction Hash:", transaction.calculate_hash())

# Sign the transaction
for tx in tx_pool:
    tx.hash_transaction()
    print("Transaction Signature:", tx.signature)



# Validate the transaction
# is_valid = transaction.is_valid()
# print("Is Transaction Valid?", is_valid)