import asyncio
import logging
from blockchain.blockchain import Blockchain
from blockchain.proof_of_work import ProofOfWork
from blockchain.miner import Miner
from network.host import Host
from network.message import Message
from _config.app_config import AppConfig


class BlockchainNode:
    def __init__(self, config_path: str=None):
        """
        Initializes the blockchain node with all core components.
        """
        self.config = AppConfig()  # Load configuration
        network_config = self.config.get_network_config()
        mining_config = self.config.get_mining_config()
        nbits = mining_config.get("nbits", "0x1e0ffff0")

        # Instantiate core components
        self.proof_of_work = ProofOfWork(nbits=nbits)
        self.blockchain = Blockchain(self.proof_of_work)
        self.miner = Miner(self.blockchain)

        # Network setup
        self.host = Host(network_config)

    async def start(self):
        """
        Start the blockchain node.
        """
        logging.info("Starting blockchain node...")
        try:
            # Start the network host
            await self.host.start()

            # Start mining and broadcasting blocks
            asyncio.create_task(self.mine_and_broadcast())

            # Keep the node running
            while True:
                await asyncio.sleep(10)
        except asyncio.CancelledError:
            logging.info("Shutdown initiated via KeyboardInterrupt.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

    async def mine_and_broadcast(self):
        """
        Mines blocks and broadcasts them to peers.
        """
        while True:
            new_block = self.miner.mine_block()
            if new_block:
                logging.info(f"New block mined: Index = {new_block.index}, Hash = {new_block.compute_hash()}")

                # Broadcast the new block to peers
                block = new_block.to_dict()
                message = Message(content_type="BK", content=block)
                await self.host.broadcast_message(message)

            await asyncio.sleep(1)  # Adjust mining frequency as needed

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
    # logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

    config_path = "_config/config.json"  # Optional Path to configuration file
    node = BlockchainNode()

    try:
        asyncio.run(node.start())
    except KeyboardInterrupt:
        logging.info("Shutting down node...")
        asyncio.run(node.shutdown())