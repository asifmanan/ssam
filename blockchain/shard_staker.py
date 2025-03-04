import uuid
import hashlib
import logging
from typing import List
from blockchain.shard_block import ShardBlock
from transaction.transaction_manager import TransactionManager
from blockchain.blockchain import Blockchain
from blockchain.main_block import MainBlock

class ShardStaker:
    def __init__(self, transaction_manager: TransactionManager, blockchain: Blockchain, node_name: str):
        """
        Initializes the Staker Node.
        :param transaction_manager: The Transaction Manager object.
        :param blockchain: The Blockchain object.
        """
        self.shard_block_list = []
        self.blockchain = blockchain
        self.stakes = {}
        self.staker_node_name = node_name
        self.transaction_manager = transaction_manager
        staker_signature = uuid.uuid4().hex
        self.staker_signature = f"{self.staker_node_name}:{staker_signature}"

    def initialize_stakes(self, stake_info):
        """
        Initialize the stakes for the stakers.
        :param stake_info: A dictionary of staker IDs and their stakes.
        """
        self.stakes = stake_info
        
    
    def add_stake(self, staker_id, amount):
        """
        Add a stake to the staker.
        :param staker_id: The ID of the staker.
        :param amount: The amount to stake.
        """
        if staker_id not in self.stakes:
            self.stakes[staker_id] = amount
        else:
            self.stakes[staker_id] += amount

    def select_staker(self):
        """
        Deterministically selects a staker based on their stake and the previous block hash.
        :return: The selected staker ID.
        """
        if not self.stakes or sum(self.stakes.values()) == 0:
            return None

        # Get the hash of the previous block
        previous_block = self.blockchain.get_last_block()
        previous_block_hash = previous_block.compute_hash()
        epoch = previous_block.index + 1

        # Sort staker IDs to ensure consistent ordering
        sorted_stakers = sorted(self.stakes.keys())

        # Combine the previous block hash with sorted staker IDs
        combined_string = previous_block_hash + ''.join(sorted_stakers)
        combined_hash = hashlib.sha256(combined_string.encode()).hexdigest()

        # Convert the hash to a deterministic "random" number
        hash_number = int(combined_hash, 16)

        # Use weighted selection based on stakes
        total_stake = sum(self.stakes.values())
        cumulative_weight = 0

        for staker in sorted_stakers:
            stake_weight = self.stakes[staker]
            cumulative_weight += stake_weight
            if hash_number % total_stake < cumulative_weight:
                return staker, epoch

    
    def validate_shard_block(self, shard_block: ShardBlock):
        """
        Validates a shard block from a Shard Miner.
        :param shard_block: The shard block submitted by a Shard Miner.
        """
        # Verify the Merkle root
        calculated_merkle_root = self.transaction_manager.calculate_merkle_root(shard_block.transactions)
        if calculated_merkle_root != shard_block.merkle_root:
            return False

        # Add the shard block to the list of received blocks
        # self.shard_block_list.append(shard_block)
        # print(f"Shard block from Miner {shard_block.miner_id} verified and accepted.")
        return True
    
    def propose_main_block(self, shard_blocks: List[ShardBlock]):
        """
        Propose a new main block to the blockchain using transactions from multiple shard blocks.

        :param shard_blocks: A list of ShardBlock objects.
        :return: A tuple containing a boolean indicating whether the block was added successfully and the newly added block.
        """
        if shard_blocks:
            # Collect all transactions from the shard blocks
            combined_transactions = []
            shard_data = {}
            for shard_block in shard_blocks:
                shard_data[shard_block.miner_node_name] = {
                "block_hash": shard_block.compute_hash(),
                "miner_numeric_id": shard_block.miner_numeric_id,
                "timestamp": shard_block.timestamp,
                "merkle_root": shard_block.merkle_root,
                "nonce" : shard_block.nonce,
                "nbits" : shard_block.nbits,
                }
                combined_transactions.extend(shard_block.transactions)

            # Calculate a single Merkle root for all transactions
            transaction_merkle_root = self.transaction_manager.calculate_merkle_root(combined_transactions)

            # Create and propose the new main block
            new_block = self.blockchain.create_block(
                staker_signature=self.get_stacker_signature(),
                tx_root=transaction_merkle_root,
                shard_data=shard_data,
                transactions=combined_transactions,
            )
            return self.blockchain.add_block(new_block), new_block
        else:
            print("No shard blocks provided for proposing the main block.")
            return None, None
    
    # def get_shard_block(self):
    #     """
    #     Combines all transactions from received shard blocks into a main chain block.
    #     :return: A new Block object.
    #     """
    #     return self.shard_block_list.pop()
        
    def get_stacker_signature(self):
        """
        Get the staker signature.
        :return: The staker signature.
        """
        return self.staker_signature
    
    def receive_main_block(self, message, block_sender):
        """
        Receive a main block from the main chain.
        """
        if message.get_content_type() == "MAIN_BLOCK":
            message_payload = message.get_content()
            main_block = MainBlock.from_dict(message_payload)

            is_added = self.blockchain.add_block(main_block)

            if is_added:
                logging.info(f"Block proposed by {block_sender} added Block {main_block.index} to the blockchain.")
                return True, main_block
            else:
                logging.info(f"Staker {block_sender} rejected the block.")
                return False
    
    def process_shard_block(self, message):
        if message.get_content_type() == "SHARD_BLOCK":
            message_payload = message.get_content()
            shard_block = ShardBlock.from_dict(message_payload)
            logging.info(f"Staker {self.staker_node_name} received shard block from {shard_block.miner_node_name}.")
            is_valid = self.validate_shard_block(shard_block)
            if is_valid:
                return True, shard_block
    
            else:
                logging.warning(f"Staker {self.staker_node_name} rejected the block.")
                return False, None


                
        
        