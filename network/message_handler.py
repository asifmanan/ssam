import logging
import json
from network.message import Message
from network.peer import Peer


class MessageHandler:
    def __init__(self):
        self.shard_blocks = []
        self.main_blocks = []
        self.transactions = []
        self.other = []

    async def handle_message(self, sender: str, message: str):
        """
        Handle incoming messages from peers. 

        :param: sender (str): The address of the sender.
        :param: message (str): The message content.
        """
        try:
            # Parse the message into a Message object
            parsed_message = Message.from_json(message)
            content_type = parsed_message.get_content_type()
            if content_type == "SHARD_BLOCK":
                logging.info(f"Received SHARD_BLOCK from {sender}")
                await self.add_shard_block(parsed_message.get_content())

            elif content_type == "TRANSACTION":
                logging.info(f"Received TRANSACTION from {sender}")
                await self.add_transaction(parsed_message.get_content())

            elif content_type == "MAIN_BLOCK":
                logging.info(f"Received MAIN_BLOCK from {sender}")
                await self.add_main_block(parsed_message.get_content())

            else:
                logging.warning(f"Unknown message type from {sender}: {content_type}")

        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON message from {sender}: {e}")

        except Exception as e:
            logging.error(f"Failed to handle message from {sender}: {e}")
    
    async def add_shard_block(self, shard_block):
        """
        Add a shard block to the list of shard blocks.
        :params: shard_block (ShardBlock): The shard block to add.
        """
        self.shard_blocks.append(shard_block)

    async def get_shard_block(self):
        """
        Get the list of shard blocks.
        """
        return self.shard_blocks.pop() if self.shard_blocks else None

    async def add_main_block(self, main_block):
        """
        Add a main block to the list of main blocks.
        :params: main_block (MainBlock): The main block to add.
        """
        self.main_blocks.append(main_block)
    
    async def get_main_block(self):
        """
        Get the list of main blocks.
        """
        return self.main_blocks.pop() if self.main_blocks else None

    async def add_transaction(self, transaction):
        """
        Add a transaction to the list of transactions.
        :params: transaction (Transaction): The transaction to add.
        """
        self.transactions.append(transaction)
    
    async def get_transaction(self):
        """
        Get the list of transactions.
        """
        return self.transactions.pop() if self.transactions else None
