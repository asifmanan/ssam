import asyncio
import logging
from blockchain.blockchain import Blockchain
from blockchain.proof_of_work import ProofOfWork
from blockchain.miner import Miner
from network.host import Host
from network.message import Message


class BlockchainNode:
    def __init__(self, config_path):
        """
        Initializes the blockchain node with all core components.
        """
        self.config_path = config_path

        # Instantiate core components
        self.proof_of_work = ProofOfWork()
        self.blockchain = Blockchain(self.proof_of_work)
        self.miner = Miner(self.blockchain)

        # Network setup
        self.host = Host(config_path)

    async def start(self):
        """
        Start the blockchain node.
        """
        logging.info("Starting blockchain node...")

        # Start the network host
        await self.host.start()

        # Start peer discovery
        await self.host.start_peer_discovery()

        # Announce this node to peers
        await self.host.peer_discovery.announce_peer()

        # Start mining and broadcasting blocks
        asyncio.create_task(self.mine_and_broadcast())

        # Keep the node running
        while True:
            await asyncio.sleep(10)

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
                print(f"Message: {message}")
                await self.host.broadcast_message(message)

            await asyncio.sleep(1)  # Adjust mining frequency as needed

    async def shutdown(self):
        """
        Shutdown the blockchain node gracefully.
        """
        await self.host.stop()
        logging.info("Blockchain node stopped.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    config_path = "config.json"  # Path to configuration file
    node = BlockchainNode(config_path)

    try:
        asyncio.run(node.start())
    except KeyboardInterrupt:
        logging.info("Shutting down node...")
        asyncio.run(node.shutdown())