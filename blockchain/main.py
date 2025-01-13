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
from blockchain.main_block import MainBlock

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
                message = await self.host.message_handler.get_control_message()
                if message.get_content_type() == "CONTROL":
                    control_message = message.get_content()
                
                if control_message:
                    mining_allowed = self.process_control_message(control_message)

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

    def process_control_message(self, control_message):
        action = control_message.get("action")
        shard = control_message.get("shard")
        if shard == self.shard_name:
            if action == "START":
                logging.info(f"Miner {self.node_name} received START message. Mining allowed.")
                return True
                
            elif action == "STOP":
                logging.info(f"Miner {self.node_name} received STOP message. Mining halted.")
                return False
                
    
    async def run_staker(self, shard_peers):
        """
        Run Shard Staker Node.
        """
        shard_staker = ShardStaker(transaction_manager=self.transaction_manager, blockchain=self.blockchain, node_name=self.node_name)
        shard_staker.initialize_stakes(self.stake_info)

        while True:
            try:
                # Determine active shard
                mining_turn = False
                selected_staker, epoch = shard_staker.select_staker()
                logging.info(f"Selected staker: {selected_staker} for epoch {epoch}.")
                
                if selected_staker != self.node_name:
                    logging.info(f"Staker {self.node_name} waiting for Main Block.")
                    
                    message = await self.host.message_handler.get_main_block()  # Wait for main block message
                    is_added = shard_staker.receive_main_block(message, block_sender=selected_staker)
                    
                    continue
                         
                elif selected_staker == self.node_name:
                    # The part of the program which will execute if the selected staker is the current node

                    mining_turn = True                
                    logging.info(f"Shard {self.shard_name} selected for mining.")
                    
                    shard_peers = self.config.get_peers_for_shard(self.shard_name)

                    # Wait for shard block messages
                    if mining_turn == True:
                        for peer in shard_peers:
                            if "miner" in peer:
                                miner_peer = Peer(*peer.split(":"))
                                control_message = Message.generate_start_message(shard_name=self.shard_name, epoch=epoch, node_name=self.node_name)
                                await self.host.send_message(miner_peer, control_message)

                        message = await self.host.message_handler.get_shard_block()
                        is_valid, shard_block = shard_staker.process_shard_block(message)

                        
                        if is_valid:
                            is_accepted, new_main_block = shard_staker.propose_block(shard_block=shard_block)
                        
                        for peer in shard_peers:
                            if "miner" in peer:
                                miner_peer = Peer(*peer.split(":"))
                                control_message = Message.generate_stop_message(shard_name=self.shard_name, epoch=epoch, node_name=self.node_name)
                                await self.host.send_message(miner_peer, control_message)

                        staker_peers = self.config.get_other_stakers(self.node_name)
                        if is_accepted:
                            for peer in staker_peers:
                                staker_peer = Peer(*peer.split(":"))
                                message = Message(content_type="MAIN_BLOCK", content=new_main_block.to_dict(), sender=self.node_name)
                                await self.host.send_message(staker_peer, message)
                                logging.info(f"Staker {self.node_name} sent main block to {peer}.")
                
                # Wait before rotating to the next shard
                await asyncio.sleep(3)  
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