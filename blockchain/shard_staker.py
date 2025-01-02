import uuid
from blockchain.shard_block import ShardBlock
from transaction.transaction_manager import TransactionManager
from blockchain.blockchain import Blockchain

class ShardStaker:
    def __init__(self, transaction_manager: TransactionManager, blockchain: Blockchain):
        """
        Initializes the Staker Node.
        """
        self.shard_block_list = []
        self.blockchain = blockchain
        self.transaction_manager = transaction_manager
        self.staker_signature = uuid.uuid4().hex

    def validate_shard_block(self, shard_block: ShardBlock):
        """
        Validates a shard block from a Shard Miner.
        :param shard_block: The shard block submitted by a Shard Miner.
        """
        # Verify the Merkle root
        calculated_merkle_root = self.transaction_manager.calculate_merkle_root(shard_block.transactions)
        if calculated_merkle_root != shard_block.merkle_root:
            raise ValueError(f"Merkle root mismatch! Expected {shard_block.merkle_root}, got {calculated_merkle_root}")

        # Add the shard block to the list of received blocks
        self.shard_block_list.append(shard_block)
        print(f"Shard block from Miner {shard_block.miner_id} verified and accepted.")
    
    def get_stacker_signature(self):
        return self.staker_signature
    
    def get_shard_data(self):
        """
        Combines all transactions from received shard blocks into a main chain block.
        :return: A new Block object.
        """
        shard_miners_count = self.transaction_manager.get_num_miners()
        # confirm if all shard blocks have been received
        if len(self.shard_block_list) == shard_miners_count:
            all_transactions = []
            for shard_block in self.shard_block_list:
                all_transactions.extend(shard_block.transactions)

            tx_root = self.transaction_manager.calculate_merkle_root(all_transactions)
            return {"tx_root": tx_root, 
                    "shard_miners_count":shard_miners_count, 
                    "transactions": all_transactions,
                    "staker_signature": self.staker_signature,
                    }
        
        else:
            return None
        