import asyncio
import hashlib
import logging
from network.message import Message

class MessageHandler:
  def __init__(self, host):
    """
    Initialize the message handler.
    :param host: reference to the Host instance for managing peer connections.
    """
    self.host = host

  async def send_message(self, peer_id: str, message: str) -> None:
    """
    Send a message to a peer via WebRTC.
      
    :param sender_id: The unique identifier of the peer
    :param message: The message to send
    """
    try:
        pc = self.host.peer_manager.get_peer_connection(peer_id)
        if not pc or "data_channel" not in pc.dataChannels:
            raise Exception(f"No active connection or data channel with peer {peer_id}")

        channel = pc.dataChannels["data_channel"]
        channel.send(message)
        logging.info(f"Message sent to {peer_id}: {message}")

    except Exception as e:
        logging.error(f"Failed to send message to {peer_id}: {e}")
  
  async def handle_incoming(self, sender: str, message:str):
    """
    Process incomming messages from peers.

    :param sender_id: The unique identifier of the peer who sent the message.
    :param message: The content of the incoming message.
    """
    try:
      parsed_message = Message.from_json(message)
      # Logic for handling different types of messages
      if parsed_message.get_content_type() == "BK":
        print(f"Received a new block from {sender}")
        # Can add blockchain specific logic here
      elif parsed_message.get_content_type("TX"):
        print(f"Received a new transaction from {sender}: {message}")
        # Can add transaction specific logic here
      else:
        print(f"Received an unknown message type from {sender}: {message}")
    except Exception as e:
      # logging.error(f"Failed to handle incoming message: {e}")
      print(f"Failed to handle incoming message from {sender}: {e}")

  async def setup_channel_listeners(self, sender: str, pc):
    """
    Set up listeners for a WebRTC peer connection to handle incoming messages.

    :param peer_id: The unique identifier of the peer.
    :param pc: The WebRTC peer connection object.
    """
    try:
        @pc.on("datachannel")
        def on_datachannel(channel):
            pc.dataChannels[channel.label] = channel

            @channel.on("open")
            def on_open():
                logging.info(f"Data channel with {sender} is open.")

            @channel.on("message")
            def on_message(message):
                asyncio.create_task(self.handle_incoming(sender, message))

    except Exception as e:
        logging.error(f"Failed to set up channel listeners for {sender}: {e}")
  
  def verify_signature(self, message: str, signature: str, public_key: str) -> bool:
    """
    Verify the signature of an incoming message.

    :param message: The message content.
    :param signature: The cryptographic signature of the message.
    :param public_key: The public key of the sending peer who signed the message.
    :return: True if the signature is valid, False otherwise.
    """
    try:
      # Placeholder logic for verifying the signature
      # Need to use cyptographic libraries for real-world applications
      message_hash = hashlib.sha256(message.encode()).hexdigest()
      # Verify the signature
      # Can add signature verification logic here
      return message_hash == signature
    except Exception as e:
      print(f"Failed to verify signature: {e}")
      return False