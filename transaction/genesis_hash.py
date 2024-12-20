import json
import hashlib
from transaction.transaction import Transaction
with open("transaction/genesis_tx.json", "r") as f:
    genesis = json.load(f)
    tx = Transaction.from_dict(genesis[0])
    print(tx.metadata)
    genesis_hash = tx.calculate_hash()
    print(genesis_hash)