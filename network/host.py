import asyncio
import logging
from network.peer_manager import PeerManager
from network.message import Message
from network.peer import Peer
from network.message_handler import MessageHandler


class Host:
    def __init__(self, network_config: dict):
        """
        Initialize the Host with peer management.
        :param network_config: The network configuration.
        """
        peers_list = network_config.get("peers", [])
        self.peer_manager = PeerManager(peers_list)
        self.message_handler = MessageHandler()
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
                    logging.warning(f"Failed to connect to {peer}, retrying in 5 seconds ({3 - retries}/3)")
                    await asyncio.sleep(5)
            else:
                logging.error(f"Failed to connect to {peer} after 3 retries.")

    async def listen_for_connections(self):
        """
        Listen for incoming connections on the local address.
        """
        server = await asyncio.start_server(self.handle_incoming_connection, "0.0.0.0", int(self.peer_manager.this_peer.port))
        logging.info(f"Listening for incoming connections at {self.peer_manager.this_peer}")
        async with server:
            await server.serve_forever()

    async def handle_incoming_connection(self, reader, writer):
        """
        Handle an incoming connection from a peer.
        :param reader: The StreamReader object.
        :param writer: The StreamWriter object.
        reference: https://docs.python.org/3/library/asyncio-stream.html#asyncio.StreamReader
        """
        peer_address = writer.get_extra_info("peername")
        # logging.info(f"Incoming connection from {peer_address}")
        self.peer_connections[peer_address] = (reader, writer)

        while True:
            try:    
                data = await reader.readline()
                if not data:
                    logging.info(f"Connection closed by {peer_address}")
                    break
                message = data.decode().strip()
                asyncio.create_task(self.handle_message(peer_address, message))
            except Exception as e:
                logging.error(f"Error processing message from {peer_address}: {e}")
                break

    async def handle_message(self, sender: str, message: str):
        """
        Handle an incoming message from a peer.
        :param sender: The address of the sender.
        :param message: The message content.
        """
        await self.message_handler.handle_message(sender=sender, message=message)

    async def send_message(self, peer: Peer, message: Message):
        """
        Send a message to a peer.
        :param peer: The peer to send the message to.
        :param message: The message to send.

        References: 
        https://docs.python.org/3/library/asyncio-stream.html#asyncio.StreamWriter.write
        https://stackoverflow.com/questions/19143360/python-writing-to-and-reading-from-serial-port
        https://stackoverflow.com/questions/44056846/how-to-read-and-write-from-a-com-port-using-pyserial

        """
        try:
            if str(peer) not in self.peer_connections:
                raise Exception(f"No active connection to {peer}")
            
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
        :param message: The message to broadcast.
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