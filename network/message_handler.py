import logging
import json
from network.message import Message
import asyncio


class MessageHandler:
    def __init__(self):
        self.shard_blocks = asyncio.Queue()
        self.main_blocks = asyncio.Queue()
        self.transactions = asyncio.Queue()
        self.control_message = asyncio.Queue()

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
                logging.info(f"[MessageHandler (handle_message)] Received SHARD_BLOCK from {sender}")
                shard_block = parsed_message.get_content()
                await self.add_shard_block(shard_block)

            elif content_type == "CONTROL":
                logging.info(f"Received CONTROL message from {sender}")
                message_content = parsed_message.get_content()
                await self.add_control_message(message_content)

            elif content_type == "TRANSACTION":
                logging.info(f"Received TRANSACTION from {sender}")
                await self.add_transaction(parsed_message)

            elif content_type == "MAIN_BLOCK":
                logging.info(f"Received MAIN_BLOCK from {sender}")
                await self.add_main_block(parsed_message)

            else:
                logging.warning(f"Unknown message type from {sender}: {content_type}")

        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON message from {sender}: {e}")

        except Exception as e:
            logging.error(f"Failed to handle message from {sender}: {e}")
    
    async def add_shard_block(self, shard_block):
        """
        Add a shard block to the Shard Message Queue.
        :params: shard_block (ShardBlock): The shard block to add.
        """
        await self.shard_blocks.put(shard_block)

    async def get_shard_block(self):
        """
        Get the Shard block from the Shard Message Queue.
        """
            
        shard_block = await self.shard_blocks.get()
        return shard_block

    async def add_main_block(self, main_block):
        """
        Add a main block to the Queue.
        :params: main_block (MainBlock): The main block to add.
        """
        await self.main_blocks.put(main_block)
    
    async def get_main_block(self):
        """
        Get the Main block from the Queue.
        """
        main_block = await self.main_blocks.get()
        return main_block

    async def add_control_message(self, content):
        """
        Add a control message to the Queue.
        :params: control_message: The control message to add.
        """
        await self.shard_blocks.put(content)
    
    
    async def get_control_message(self):
        """
        Get the latest control message.
        """
        control_message = await self.shard_blocks.get()
        return control_message
    
    
    async def add_transaction(self, transaction):
        """
        Add a transaction to the Queue.
        :params: transaction (Transaction): The transaction to add.
        """
        await self.transactions.put(transaction)
    
    async def get_transaction(self):
        """
        Get and return the transaction.
        """
        transaction = await self.transactions.get()
        return transaction
