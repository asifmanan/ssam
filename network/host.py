import asyncio
import logging
import json
from network.peer_manager import PeerManager
from network.message import Message
from network.peer import Peer


class Host:
    def __init__(self, network_config: dict):
        """
        Initialize the Host with peer management.
        """
        peers_list = network_config.get("peers", [])
        self.peer_manager = PeerManager(peers_list)
        self.peer_connections = {}

    async def start(self):
        """
        Start the host, establish connections to peers, and listen for incoming connections.
        """
        asyncio.create_task(self.listen_for_connections())
        await self.connect_to_peers()

    async def connect_to_peers(self):
        """
        Connect to all peers listed in the PeerManager with retries.
        """
        for peer in self.peer_manager.get_peers():
            retries = 3
            while retries > 0:
                try:
                    reader, writer = await asyncio.open_connection(peer.get_hostname(), int(peer.get_port()))
                    self.peer_connections[str(peer)] = (reader, writer)
                    logging.info(f"Connected to peer {peer}")
                    break
                except Exception as e:
                    retries -= 1
                    logging.warning(f"Failed to connect to {peer}, retrying in 2 seconds ({3 - retries}/3)")
                    await asyncio.sleep(2)
            else:
                logging.error(f"Failed to connect to {peer} after 3 retries.")

    async def listen_for_connections(self):
        """
        Listen for incoming connections on the local address.
        """
        # server = await asyncio.start_server(self.handle_incoming_connection, self.peer_manager.this_peer.host, int(self.peer_manager.this_peer.port))
        server = await asyncio.start_server(self.handle_incoming_connection, "0.0.0.0", int(self.peer_manager.this_peer.port))
        logging.info(f"Listening for incoming connections at {self.peer_manager.this_peer}")
        async with server:
            await server.serve_forever()

    async def handle_incoming_connection(self, reader, writer):
        """
        Handle an incoming connection from a peer.
        """
        peer_address = writer.get_extra_info("peername")
        logging.info(f"Incoming connection from {peer_address}")
        self.peer_connections[peer_address] = (reader, writer)

        while True:
            try:    
                data = await reader.readline()
                if not data:
                    break
                message = data.decode().strip()
                asyncio.create_task(self.handle_message(peer_address, message))
            except Exception as e:
                logging.error(f"Error processing message from {peer_address}: {e}")
                break

    async def handle_message(self, peer_address: str, message: str):
        """
        Handle an incoming message from a peer.

        Args:
            peer_address (str): The address of the peer sending the message.
            message (str): The content of the message received.
        """
        try:
            # Parse the message into a Message object
            parsed_message = Message.from_json(message)
            # logging.info(f"Received message from {peer_address}: {parsed_message}")

            if parsed_message.content_type == "BK":  # Block message
                logging.info(f"Received a new block from {peer_address}, (Block Index: {parsed_message.content["index"]})")
                # Handle the block (validate and add to blockchain)
            elif parsed_message.content_type == "TX":  # Transaction message
                logging.info(f"Received a transaction from {peer_address}")
                # Handle the transaction (add to transaction pool)
            else:
                logging.warning(f"Unknown message type from {peer_address}: {parsed_message.content_type}")
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON message from {peer_address}: {e}")
        
        except Exception as e:
            logging.error(f"Failed to process message from {peer_address}: {e}")

    async def send_message(self, peer: Peer, message: Message):
        """
        Send a message to a peer.
        """
        try:
            if str(peer) not in self.peer_connections:
                raise Exception(f"No active connection to {peer}")
            
            # connection = self.peer_connections.get(str(peer))
            # if not connection:
            #     raise Exception(f"No active connection to {peer}")
            if not message or not isinstance(message, Message):
                raise ValueError("Message is invalid or None")
            
            _, writer = self.peer_connections[str(peer)]
            
            serialized_message = message.to_json()
            if not serialized_message.strip():
                raise ValueError("Serialized message is empty")
            
            encoded_message = serialized_message.encode() + b"\n"
            
            writer.write(encoded_message)
            await writer.drain()
            
            logging.info(f"Message sent to {peer}, Message Type: {message.content_type}")
        except Exception as e:
            logging.error(f"Failed to send message to {peer}: {e}")

    async def broadcast_message(self, message: Message):
        """
        Broadcast a message to all connected peers.
        """
        for peer in self.peer_manager.get_peers():
            asyncio.create_task(self.send_message(peer, message))

    async def stop(self):
        """
        Stop the host and clean up resources.
        """
        logging.info("Stopping host...")
        # Close all peer connections
        for peer, (reader, writer) in self.peer_connections.items():
            writer.close()
            await writer.wait_closed()
            logging.info(f"Closed connection to {peer}")