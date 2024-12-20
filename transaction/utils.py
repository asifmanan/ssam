import json
from transaction.transaction import Transaction

def load_genesis_transactions_file():
        """
        Load transactions for the genesis block.
        :return: List of Transaction objects.
        """
        try:
            with open("transaction/genesis_tx.json", 'r') as f:
                data = json.load(f)
                return [Transaction(**tx) for tx in data]
        except FileNotFoundError:
            return []
        
def load_genesis_transactions():
    """
    Load transactions for the genesis block.
    :return: List of Transaction objects.
    """
    tx_data = [
              {
                "sender": "Network",
                "recipient": "Public",
                "amount": 100,
                "timestamp": "1734129224.311285",
                "metadata": {
                  "sub_nonce": 0,
                  "text": "UK economy shrinks for second month in a row",
                  "date": "2024-12-13",
                  "source": "https://www.bbc.co.uk/news/articles/cq5lw84w1yeo"
                },
                "signature": "1011a88e4e9231ad320625b235a22997ba68d99db47a808dcc059c07395082eb"
              },
          ]
    tx_list = [Transaction(**tx) for tx in tx_data]
    return tx_list