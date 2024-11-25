from blockchain.blockchain import Blockchain
if __name__ == "__main__":
  new_chain = Blockchain()
  last_block = new_chain.get_last_block()
  print("Hash of last Block: " + last_block.hash)
