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

        # self.node_name = os.getenv("NODE_NAME")
        # self.shard_name = os.getenv("SHARD")

        # self.host = Host(self.network_config)

        self.transactions = TransactionManager.load_transactions()
        self.transaction_manager = TransactionManager(transactions=self.transactions, num_miners=2)

        self.blockchain = Blockchain(transaction_manager=self.transaction_manager)

    async def start(self):
        """
        Start the blockchain node.
        """
        # Stake Info
        print(f"stake info: {self.stake_info}")

        # Initialize Stakes
        node_name = "staker10"
        shard_staker = ShardStaker(transaction_manager=self.transaction_manager, blockchain=self.blockchain, node_name=node_name)
        
        
        shard_staker.initialize_stakes(self.stake_info)
        print(f"Stakes after init: {shard_staker.stakes}")

        selected_staker = shard_staker.select_staker()
        print(f"Selected staker: {selected_staker}")
        

if __name__ == "__main__":
    node = BlockchainNode()
    asyncio.run(node.start())