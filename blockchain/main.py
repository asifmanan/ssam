import os
import asyncio
import logging
import threading
from webapp.blockchain_view import start_webserver

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

# ssam - Sharded Stake Aggregation Mechanism/Model
# ENHANCING BLOCKCHAIN SCALABILITY AND TRANSACTION EFFICIENCY USING SHARDED CHAIN ARCHITECTURE

class BlockchainNode:
    def __init__(self):
        """
        Initializes the node with all core components.
        """
        self.config = AppConfig(config_file_path="_config/config.json")
        self.network_config = self.config.get_network_config()
        self.shard_config = self.config.get_shard_config()
        self.stake_info = self.config.get_stake_info()
        self.mining_config = self.config.get_mining_config()
        self.nbits = self.mining_config.get("nbits")

        self.node_name = os.getenv("NODE_NAME")
        self.shard_name = os.getenv("SHARD")

        self.num_of_miners = self.config.get_number_of_miners(self.shard_name)
        self.miner_id_map = self.generate_miner_id_map()

        self.host = Host(self.network_config)
        self.transactions = TransactionManager.load_transactions()
        self.transaction_manager = TransactionManager(transactions=self.transactions, num_miners=self.num_of_miners)

        self.blockchain = Blockchain()

        if self.node_name.startswith("staker"):
            flask_thread = threading.Thread(
                target=start_webserver, args=(self.blockchain, self.node_name), daemon=True
            )
            flask_thread.start()
            logging.info(f"Flask webserver started for {self.node_name}.")

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

            # logging.info(f"Node {self.node_name} belongs to {self.shard_name} with staker {staker_address}.")

            if self.node_name.startswith("miner"):
                await self.run_miner(staker_address)
            elif self.node_name.startswith("staker"):
                await self.run_staker(shard_peers)
        except Exception as e:
            logging.error(f"Unexpected error occured in BlockchainNode.start(): {e}")

    async def run_miner(self, staker_address):
        """
        Run Shard Miner Node.
        """
        shard_miner = ShardMiner(miner_numeric_id=self.get_miner_id(), 
                                 miner_node_name=self.node_name, 
                                 num_miners=self.num_of_miners, 
                                 transactions=self.transactions, 
                                 nbits=self.nbits)
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
                    mining_allowed = False
                    logging.info(f"Miner {self.node_name} sent shard block to Staker {staker_address}.")
                    await asyncio.sleep(1)
            except Exception as e:
                logging.error(f"Error in miner operation: {e}")
            

    def process_control_message(self, control_message):
        """
        Process the control message to determine if mining is allowed.
        : param control_message: The control message to process.
        : return: True if mining is allowed, False otherwise.
        """
        action = control_message.get("action")
        shard = control_message.get("shard")
        if shard == self.shard_name:
            if action == "START":
                logging.info(f"Miner {self.node_name} received START message. Mining allowed.")
                return True
                
            elif action == "STOP":
                # logging.info(f"Miner {self.node_name} received STOP message. Mining halted.")
                return False
                
    def generate_miner_id_map(self) -> dict:
        """
        Generate a mapping of miner node names to zero-based IDs for the current shard.
        :return: A dictionary mapping miner node names to their IDs.
        """
        shard_peers = self.shard_config.get(self.shard_name, [])
        miner_peers = [peer.split(":")[0] for peer in shard_peers if "miner" in peer]
        return {miner: idx for idx, miner in enumerate(miner_peers)}
    
    def get_miner_id(self) -> int:
        """
        Retrieve the miner ID for the current node.
        :return: The zero-based ID of the miner.
        """
        if self.node_name in self.miner_id_map:
            return self.miner_id_map[self.node_name]
        raise ValueError(f"Node name {self.node_name} not found in miner ID map.")
    
    
    
    async def run_staker(self, shard_peers):
        """
        Run Shard Staker Node.
        """
        shard_staker = ShardStaker(transaction_manager=self.transaction_manager, blockchain=self.blockchain, node_name=self.node_name)
        shard_staker.initialize_stakes(self.stake_info)
        genesis_block = self.blockchain.get_last_block()
        self.blockchain.write_to_json(node_name=self.node_name, block=genesis_block)
        current_epoch = genesis_block.index + 1

        while True:
            try:
                # Determine active shard
                mining_turn = False
                selected_staker, next_epoch = shard_staker.select_staker()
                logging.info(f"Selected staker: {selected_staker} for epoch {next_epoch}.")
                
                if selected_staker != self.node_name:
                    # This part of the program will execute if the selected staker not the current node
                    logging.info(f"Staker {self.node_name} waiting for Main Block.")
                    
                    message = await self.host.message_handler.get_main_block()  # Wait for main block message
                    is_added, received_main_block = shard_staker.receive_main_block(message, block_sender=selected_staker)
                    self.blockchain.write_to_json(node_name=self.node_name, block=received_main_block)
                    
                    continue
                         
                elif selected_staker == self.node_name:
                    # This part of the program will execute if the selected staker is the current node

                    mining_turn = True                
                    logging.info(f"Shard {self.shard_name} selected for mining.")
                    
                    shard_peers = self.config.get_peers_for_shard(self.shard_name)

                    # Wait for shard block messages
                    if mining_turn == True:
                        for peer in shard_peers:
                            if "miner" in peer:
                                miner_peer = Peer(*peer.split(":"))
                                control_message = Message.generate_start_message(shard_name=self.shard_name, epoch=next_epoch, node_name=self.node_name)
                                await self.host.send_message(miner_peer, control_message)

                        shard_blocks=[]
                        for _ in range(self.num_of_miners):
                            message = await self.host.message_handler.get_shard_block()
                            is_valid, shard_block = shard_staker.process_shard_block(message)
                            if is_valid:
                                shard_blocks.append(shard_block)
                            else:
                                logging.warning(f"Invalid shard block received: {message}")

                        if len(shard_blocks) == self.num_of_miners:
                            is_accepted, new_main_block = shard_staker.propose_main_block(shard_blocks=shard_blocks)
                            self.blockchain.write_to_json(node_name=self.node_name, block=new_main_block)
                            
                        
                        for peer in shard_peers:
                            if "miner" in peer:
                                miner_peer = Peer(*peer.split(":")) #Unpack. 
                                control_message = Message.generate_stop_message(shard_name=self.shard_name, epoch=next_epoch, node_name=self.node_name)
                                await self.host.send_message(miner_peer, control_message)

                        staker_peers = self.config.get_other_stakers(self.node_name)
                        if is_accepted:
                            for peer in staker_peers:
                                staker_peer = Peer(*peer.split(":"))
                                message = Message(content_type="MAIN_BLOCK", content=new_main_block.to_dict(), sender=self.node_name)
                                await self.host.send_message(staker_peer, message)
                                logging.info(f"Staker {self.node_name} sent main block to {peer}.")
                
                # Wait before rotating to the next round
                await asyncio.sleep(3)  
            except Exception as e:
                logging.error(f"Error in staker operation: {e}")

    async def shutdown(self):
        """
        Shutdown the blockchain node gracefully.
        """
        await self.host.stop()
        logging.info("Blockchain node stopped.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    node = BlockchainNode()

    try:
        asyncio.run(node.start())
    except KeyboardInterrupt:
        logging.info("Shutting down node...")
        asyncio.run(node.shutdown())