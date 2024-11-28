import time
from blockchain.blockchain import Blockchain
from node.mining import Mining
from node.miner import Miner

if __name__ == '__main__':
  # Create a blockchain instance
  blockchain = Blockchain()

  # Create a mining instance 
  mining_instance = Mining(blockchain, node_address="my_node", owner_id="owner_x")

  # Create a miner instance 
  miner = Miner(mining_instance)

  try: 
    # Start the miner 
    print("Starting the miner...")
    miner.start_mining() 
    
    # And let it run for a while (x seconds)
    time.sleep(10)
    
  except KeyboardInterrupt: 
    print("Interrup received! Stopping Miner...")
  finally:
    print("Stopping the miner")
    miner.stop_mining()


