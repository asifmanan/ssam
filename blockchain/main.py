import os
import asyncio
import logging

from network.host import Host
from network.message import Message
from network.peer import Peer

from blockchain.shard_miner import ShardMiner
from blockchain.shard_staker import ShardStaker
from blockchain.shard_block import ShardBlock
from blockchain.main_block import MainBlock
from blockchain.blockchain import Blockchain

from transaction.transaction_manager import TransactionManager

from _config.app_config import AppConfig

# Simulation of Sharded Stake Aggregation Model (SSAM) 

"""  
The basic idea of the core blockchain application was adopted from 
(https://github.com/ratteripenta/blockchain-a-z/tree/master/notebooks) 
and then modified as per the project requirements and proposed techniques. 

Other references include:
https://en.bitcoin.it/wiki/Difficulty
https://bitcoin.stackexchange.com/questions/30467/what-are-the-equations-to-convert-between-bits-and-difficulty
https://stackoverflow.com/questions/22059359/trying-to-understand-nbits-value-from-stratum-protocol/22161019#22161019
  
"""
class BlockchainNode:
    def __init__(self):
        """
        Initializes the node with all core components.
        """
        self.config = AppConfig(config_file_path="_config/config.json")
        self.network_config = self.config.get_network_config()
        self.shard_config = self.config.get_shard_config()
        self.mining_config = self.config.get_mining_config()

        num_miners = self.shard_config["num_miners"]

        
        self.host = Host(self.network_config)
        
        self.transactions = TransactionManager.load_transactions()
        self.transaction_manager = TransactionManager(transactions=self.transactions, num_miners=num_miners)

        self.blockchain = Blockchain(transaction_manager=self.transaction_manager)

    async def start(self):
        """
        Start the blockchain node.
        """
        logging.info("Starting blockchain node...")
        try:
            await self.host.start()

            # Identify node type from environment
            node_name = os.getenv("NODE_NAME")
            if not node_name:
                raise ValueError("NODE_NAME environment variable is required to identify the node.")

            # Run the subsystem based on the node type
            if node_name.startswith("miner"):
                await self.run_miner(node_name)

            elif node_name.startswith("staker"):
                await self.run_staker()
        
        # Hanlde shutdown gracefully
        except asyncio.CancelledError:
            logging.info("Shutdown initiated via KeyboardInterrupt.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

    async def run_miner(self, node_name):
        """
        Run Shard Miner Node.
        """
        await asyncio.sleep(3)
        miner_id = int(node_name.replace("miner", ""))
        transactions = self.transactions
        
        shard_miner = ShardMiner(miner_id=miner_id, 
                                 num_miners=self.shard_config["num_miners"], 
                                 transactions=transactions)

        while True:
            # Process transactions and send shard block to Staker Node
            shard_block = shard_miner.mine_shard_block()
            staker_address = self.shard_config["staker_address"]
            message = Message(content_type="SHARD_BLOCK", content=shard_block.to_dict(), sender=f"miner{miner_id}")

            staker_peer = Peer(*staker_address.split(":"))
            await self.host.send_message(staker_peer, message)
            # logging.info(f"Shard Miner {miner_id} sent shard block to staker {staker_address}.")
            
            await asyncio.sleep(5)

    async def run_staker(self):
        """
        Run as a Staker Node.
        """
        shard_staker = ShardStaker(transaction_manager=self.transaction_manager, blockchain=self.blockchain)
        logging.info("Waiting for shard block messages...")

        while True:
            try:
                # Wait for the next shard block message
                block_data = await self.host.message_handler.get_shard_block()

                if block_data is not None:
                    logging.info(f"[MAIN (run_staker)] Received shard block {block_data}.")

                    # Process the received shard block
                    shard_block = ShardBlock.from_dict(block_data)
                    logging.info(f"Shard block from Miner {shard_block.miner_id} has a block hash {shard_block.compute_hash()}.")
                    is_valid = shard_staker.validate_shard_block(shard_block)

                    if is_valid:
                        is_block_added, added_block = shard_staker.propose_block()
                        
                        if is_block_added:
                            logging.info(f"Block added to the blockchain with index {added_block.index}.")
                        else:
                            logging.info(f"Block rejected by the blockchain")
                    else:
                        logging.info("Shard block is NOT VALID.")
                else: 
                    continue

                # else:
                #     logging.info("No shard block message received.")

            except Exception as e:
                logging.error(f"Error processing shard block message: {e}")
        

    async def shutdown(self):
        """
        Shutdown the blockchain node gracefully.
        """
        try:
            await self.host.stop()
            logging.info("Host stopped successfully.")
        except Exception as e:
            logging.error(f"Error during shutdown: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    node = BlockchainNode()

    try:
        asyncio.run(node.start())
    
    except KeyboardInterrupt:
        logging.info("Shutting down node...")
        asyncio.run(node.shutdown())