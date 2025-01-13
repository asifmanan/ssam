import os
import asyncio
import logging

from network.host import Host
from network.message import Message
from network.peer import Peer

from blockchain.shard_miner import ShardMiner
from blockchain.shard_staker import ShardStaker
from blockchain.blockchain import Blockchain
from blockchain.shard_block import ShardBlock

from transaction.transaction_manager import TransactionManager

from _config.app_config import AppConfig


class BlockchainNode:
    def __init__(self):
        """
        Initializes the node with all core components.
        """
        self.config = AppConfig(config_file_path="_config/config.json")
        self.network_config = self.config.get_network_config()
        self.shard_config = self.config.get_shard_config()
        self.stake_info = self.config.get_stake_info()

        self.node_name = os.getenv("NODE_NAME")
        self.shard_name = os.getenv("SHARD")

        self.host = Host(self.network_config)
        self.transactions = TransactionManager.load_transactions()
        self.transaction_manager = TransactionManager(transactions=self.transactions, num_miners=2)

        self.blockchain = Blockchain(transaction_manager=self.transaction_manager)

    async def start(self):
        """
        Start the blockchain node.
        """
        logging.info("Starting blockchain node...")
        try:
            await self.host.start()
            

            if not self.node_name or not self.shard_name:
                raise ValueError("NODE_NAME and SHARD environment variables are required.")

            shard_peers = self.config.get_peers_for_shard(self.shard_name)
            staker_address = self.config.get_staker_for_shard(self.shard_name)

            logging.info(f"Node {self.node_name} belongs to {self.shard_name} with staker {staker_address}.")

            if self.node_name.startswith("miner"):
                await self.run_miner(staker_address)
            elif self.node_name.startswith("staker"):
                await self.run_staker(shard_peers)
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

    async def run_miner(self, staker_address):
        """
        Run Shard Miner Node.
        """
        shard_miner = ShardMiner(miner_id=self.node_name, num_miners=2, transactions=self.transactions)
        mining_allowed = False  # Control variable for mining

        while True:
            try:
                # Wait for control messages
                control_message = await self.host.message_handler.get_control_message()
                if control_message:
                    action = control_message.get("action")
                    shard = control_message.get("shard")
                    if shard == self.shard_name:
                        if action == "START":
                            mining_allowed = True
                            logging.info(f"Miner {self.node_name} received START message. Mining allowed.")
                        elif action == "STOP":
                            mining_allowed = False
                            logging.info(f"Miner {self.node_name} received STOP message. Mining halted.")

                # Perform mining if allowed
                if mining_allowed:
                    shard_block = shard_miner.mine_shard_block()
                    staker_peer = Peer(*staker_address.split(":"))
                    message = Message(content_type="SHARD_BLOCK", content=shard_block.to_dict(), sender=self.node_name)

                    await self.host.send_message(staker_peer, message)
                    logging.info(f"Miner {self.node_name} sent shard block to Staker {staker_address}.")
                    await asyncio.sleep(5)
            except Exception as e:
                logging.error(f"Error in miner operation: {e}")
                await asyncio.sleep(5)

    async def run_staker(self, shard_peers):
        """
        Run Shard Staker Node.
        """
        shard_staker = ShardStaker(transaction_manager=self.transaction_manager, blockchain=self.blockchain)
        shard_staker.add_stake(self.node_name, self.stake_info.get(self.node_name, 0))
        logging.info(f"Staker {self.node_name} initialized with stake {self.stake_info.get(self.node_name, 0)}.")

        while True:
            try:
                # Determine active shard
                selected_staker, epoch = shard_staker.select_staker()
                logging.info(f"Selected staker: {selected_staker} for epoch {epoch}.")

                if selected_staker != self.node_name:
                    logging.info(f"Staker {self.node_name} waiting for its turn.")
                    await asyncio.sleep(5)
                    continue   

                
                logging.info(f"Shard {self.shard_name} selected for mining.")
                
                # Send START message to miners in this shard
                shard_peers = self.config.get_peers_for_shard(self.shard_name)
                for peer in shard_peers:
                    if "miner" in peer:
                        miner_peer = Peer(*peer.split(":"))
                        control_message = Message(content_type="CONTROL", content={
                            "action": "START",
                            "shard": self.shard_name,
                            "epoch": epoch
                        }, sender=self.node_name)
                        await self.host.send_message(miner_peer, control_message)

                # Wait for shard block messages
                shard_block_data = await self.host.message_handler.get_shard_block()
                if shard_block_data:
                    shard_block = ShardBlock.from_dict(shard_block_data)
                    logging.info(f"Staker {self.node_name} received shard block from {shard_block.miner_id}.")

                    if shard_staker.validate_shard_block(shard_block):
                        is_added, new_block = shard_staker.propose_block()
                        if is_added:
                            logging.info(f"Staker {self.node_name} added Block {new_block.index} to the blockchain.")
                            self.host.broadcast_message(Message(content_type="MAIN_BLOCK", content=new_block.to_dict(), sender=self.node_name))
                        else:
                            logging.warning(f"Staker {self.node_name} rejected the block.")

                # Send STOP message to miners in this shard
                for peer in shard_peers:
                    if "miner" in peer:
                        miner_peer = Peer(*peer.split(":"))
                        control_message = Message(content_type="CONTROL", content={
                            "action": "STOP",
                            "shard": self.shard_name
                        }, sender=self.node_name)
                        await self.host.send_message(miner_peer, control_message)

                # Wait before rotating to the next shard
                await asyncio.sleep(10)  
            except Exception as e:
                logging.error(f"Error in staker operation: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    node = BlockchainNode()

    try:
        asyncio.run(node.start())
    except KeyboardInterrupt:
        logging.info("Shutting down node...")
        asyncio.run(node.shutdown())