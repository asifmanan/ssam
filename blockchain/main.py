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
        miner_id = int(node_name.replace("miner", ""))
        transactions = self.transactions
        
        shard_miner = ShardMiner(miner_id=miner_id, 
                                 num_miners=self.shard_config["num_miners"], 
                                 transactions=transactions)

        while True:
            # Process transactions and send shard block to Staker Node
            shard_block = shard_miner.create_shard_block()
            staker_address = self.shard_config["staker_address"]
            message = Message(content_type="SHARD_BLOCK", content=shard_block.to_dict())

            staker_peer = Peer(*staker_address.split(":"))
            await self.host.send_message(staker_peer, message)
            logging.info(f"Shard Miner {miner_id} sent shard block to staker {staker_address}.")
            
            await asyncio.sleep(2)

    async def run_staker(self):
        """
        Run as a Staker Node.
        """
        shard_staker = ShardStaker(transaction_manager=self.transaction_manager, blockchain=self.blockchain)
        logging.info("Waiting for shard block messages...")

        while True:
            try:
                # Wait for the next shard block message
                shard_block_message = await self.host.message_handler.get_shard_block()

                if shard_block_message:
                    logging.info(f"Received shard block: {shard_block_message.content} from {shard_block_message.sender}")

                    # Process the received shard block
                    shard_block_data = shard_block_message.get_content()
                    shard_block = ShardBlock.from_dict(shard_block_data)
                    is_valid = shard_staker.validate_shard_block(shard_block)

                    if is_valid:
                        is_block_added, added_block = shard_staker.propose_block()
                        
                        if is_block_added:
                            logging.info(f"Block added to the blockchain with index {added_block.index}.")
                        else:
                            logging.info(f"Block rejected by the blockchain")

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
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

    node = BlockchainNode()

    try:
        asyncio.run(node.start())
    
    except KeyboardInterrupt:
        logging.info("Shutting down node...")
        asyncio.run(node.shutdown())