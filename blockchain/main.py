import os
import asyncio
import logging
from network.host import Host
from network.message import Message
from network.peer_manager import PeerManager
from network.peer import Peer
from blockchain.shard_miner import ShardMiner
from blockchain.shard_staker import ShardStaker
from blockchain.shard_block import ShardBlock
from transaction.transaction_manager import TransactionManager
from blockchain.main_block import MainBlock
from _config.app_config import AppConfig
from blockchain.blockchain import Blockchain

class BlockchainNode:
    def __init__(self):
        """
        Initializes the blockchain node with all core components.
        """
        self.config = AppConfig(config_file_path="_config/config.json")
        self.network_config = self.config.get_network_config()
        self.shard_config = self.config.get_shard_config()
        self.mining_config = self.config.get_mining_config()
        self.host = Host(self.network_config)

    async def start(self):
        """
        Start the blockchain node.
        """
        logging.info("Starting blockchain node...")
        try:
            # Start the network host
            await self.host.start()

            # Identify node type from environment
            
            node_name = os.getenv("NODE_NAME")
            if not node_name:
                raise ValueError("NODE_NAME environment variable is required to identify the node.")

            if node_name.startswith("miner"):
                await self.run_miner(node_name)
            elif node_name.startswith("stacker"):
                await self.run_staker()
        except asyncio.CancelledError:
            logging.info("Shutdown initiated via KeyboardInterrupt.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

    async def run_miner(self, node_name):
        """
        Run as a Shard Miner Node.
        """
        await asyncio.sleep(3)  # Wait for the staker node to initialize
        logging.INFO("Waiting for staker node to initialize...")
        miner_id = int(node_name.replace("miner", ""))
        transactions = TransactionManager.load_transactions()  # Implement loading logic as needed

        transaction_manager = TransactionManager(transactions=transactions, num_miners=self.shard_config["num_miners"])
        shard_miner = ShardMiner(miner_id=miner_id, 
                                 num_miners=self.shard_config["num_miners"], 
                                 transactions=transactions)

        # Process transactions and send shard block to Staker Node
        shard_block = shard_miner.create_shard_block()
        staker_address = self.shard_config["staker_address"]
        message = Message(content_type="SHARD_BLOCK", content=shard_block.to_dict())
        
        # print(staker_address)

        await self.host.send_message(staker_address, message)
        logging.info(f"Shard Miner {miner_id} sent shard block to staker {staker_address}.")

    async def run_staker(self):
        """
        Run as a Staker Node.
        """
        blockchain = Blockchain()  # Blockchain class handles appending to the chain
        transactions = TransactionManager.load_transactions()  # Implement loading logic as needed
        transaction_manager = TransactionManager(transactions=transactions, num_miners=self.shard_config["num_miners"])

        staker_node = ShardStaker(transaction_manager=transaction_manager, blockchain=blockchain)

        # Listen for shard blocks
        while True:
            message = await self.host.handle_message()
            if message.get_content_type() == "SHARD_BLOCK":
                shard_block_data = message.get_content()
                shard_block = ShardBlock.from_dict(shard_block_data)
                staker_node.validate_shard_block(shard_block)

            # Create the main block and append to the main chain
            shard_data = staker_node.get_shard_data()

            if shard_data:
                main_block = blockchain.create_block(staker_signature=shard_data["staker_signature"],
                                                      tx_root=shard_data["tx_root"],
                                                      transactions=shard_data["transactions"])

                main_block = MainBlock(
                    index=len(blockchain.chain) + 1,
                    timestamp="2025-01-01T12:00:00",
                    tx_root=shard_data["tx_root"],
                    previous_hash=blockchain.get_last_block().compute_hash() if blockchain.chain else "0",
                    staker_signature=staker_node.sign_block(),  
                    nbits=self.mining_config["nbits"],
                    transactions=shard_data["transactions"]
                )

                blockchain.add_block(main_block)
                logging.info(f"Staker created and added Main Block with Index: {main_block.index}.")

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