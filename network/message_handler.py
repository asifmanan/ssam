import logging
from network.message import Message
from network.peer import Peer


class MessageHandler:
    def __init__(self, host):
        self.host = host

    async def handle_message(self, sender: Peer, message: str):
        """
        Handle incoming messages from peers.
        """
        try:
            parsed_message = Message.from_json(message)
            content_type = parsed_message.get_content_type()
            if content_type == "SHARD_BLOCK":
                logging.info(f"Received SHARD_BLOCK from {sender}")
            elif content_type == "TRANSACTION":
                logging.info(f"Received TRANSACTION from {sender}")
            elif content_type == "MAIN_BLOCK":
                logging.info(f"Received MAIN_BLOCK from {sender}")
            else:
                logging.warning(f"Unknown message type from {sender}: {content_type}")
        except Exception as e:
            logging.error(f"Failed to handle message from {sender}: {e}")