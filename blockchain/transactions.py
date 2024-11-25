# A class for transactions. 

class Transactions: 
  def __init__(self):
    self.transactions = []

  def add_transaction(self, sender, receiver, amount):
    self.transactions.append({'sender': sender,
                              'receiver': receiver,
                              'amount': amount,
                              })
    
  def get_transactions(self):
    return self.transactions
  
  def clear_transactions(self):
    self.transactions = []