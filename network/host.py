import logging
import asyncio
from config import load_config
from aiortc import RTCPeerConnection, RTCSessionDescription
from network.peer_discovery import PeerDiscovery
from network.peer_manager import PeerManager
from network.message_handler import MessageHandler
from network.utils import MuxAddressParser

class Host:
  def __init__(self, config_path: str):
    # Load configuration
    config = load_config(config_path)

    self.bootstrap_nodes = config["peers"]
    listen_addr = config["listen_addr"]

    listen_port = MuxAddressParser.parse_port(listen_addr)
    self.listen_port = listen_port

    #  Initialize components
    self.peer_manager = PeerManager()
    self.peer_discovery = PeerDiscovery(self.listen_port, self.bootstrap_nodes)
    self.message_handler = MessageHandler(self)
    self.peer_connections = {} 

  async def start(self):
    """
      Start the host and begin peer discovery.
    """
    try:  
      await self.peer_discovery.start()
      print("Host started, Discovering peers...")
      # logging.info(f"Host started, Discovering peers...")
    except Exception as e:
      # logging.error(f"Failed to start host: {e}")
      print(f"Failed to start host: {e}")

  async def connect_to_peer(self, peer_addr: str) -> None:
    """
      Connect to a peer using its multiaddress.
    """
    try:
      # Create a new peer connection 
      pc = RTCPeerConnection()
      
      # To track data channels
      pc.dataChannels = {} 

      self.peer_connections[peer_addr] = pc

      # Create a data channel 
      data_channel = pc.createDataChannel("data_channel")
      pc.dataChannels["data_channel"] = data_channel

      # Handle incomming messages on the data_channel

      @data_channel.on("message")
      def on_message(message):
        print(f"Received message from {peer_addr}: {message}")

      # Create an offer and send an offer to the pper
      offer = await pc.createOffer()
      await pc.setLocalDescription(offer)

      # Use peer discovery (Kademlia DHT) to send the offer
      await self.peer_discovery.server.set(peer_addr, offer.sdp)
      # logging.info(f"Offer sent to peer {peer_addr}")
      print(f"Offer sent to peer {peer_addr}")

    except Exception as e:
      # logging.error(f"Failed to connect to {peer_addr}: {e}")
      print(f"Failed to connect to {peer_addr}: {e}")

  async def handle_incomming_offer(self, peer_addr: str, offer: str) -> None:
    """
      Handle an incoming offer from a peer.  
    """
    try:
      # Create a new peer connection
      pc = RTCPeerConnection()
      
      # Initialize data channel tracking
      pc.dataChannels = {}

      self.peer_connections[peer_addr] = pc

      # Handle comming data channels
      @pc.on("datachannel")
      def on_datachannel(channel):
        # Track the channel by its label
        pc.dataChannel[channel.label] = channel 

        @channel.on("message")
        def on_message(message):
          print(f"Received message from {peer_addr}: {message}")

      # Set the remote description using the received offer
      offer = RTCSessionDescription(sdp=offer, type="offer")
      await pc.setRemoteDescription(offer)

      # Create and send an answer
      answer = await pc.createAnswer()
      await pc.setLocalDescription(answer)

      # Use peer discovery (Kademlia DHT) to send the answer
      await self.peer_discovery.server.set(peer_addr, answer.sdp)
      print(f"Answer sent to peer {peer_addr}")

    except Exception as e:
      print(f"Failed to handle incoming offer from {peer_addr}: {e}")

  
  async def send_message(self, peer, protocol: str, message: str) -> None:
    """
        Send a message to a peer using a specific protocol.
    """
    await self.message_handler.send_message(peer, message)
  
  async def broadcast_message(self, message: str) -> None:
    """
      Broadcast a message to all connected peers.
    """
    if not self.peer_manager.list_peers():
        print("No connected peers to broadcast to.")
        return
    for peer_id in self.peer_manager.list_peers():
      try:
        # Use the message handler object to send the message
        await self.message_handler.send_message(peer_id, message)
        print(f"Message broadcasted to {peer_id}")
      except Exception as e:
        print(f"Failed to broadcast message to {peer_id}: {e}")

  def set_stream_handler(self, protocol: str, handler) -> None:
    """
      Register a handle for incoming streams.
    """
    self.host.set_stream_handler(protocol, handler)
  
  async def discover_peers(self, key: str, limit: int = 10):
    """
      Discover peers using DHT.
    """
    try:
      discovered_peers = await self.peer_discovery.discover_peers(key, limit)
      for peer in discovered_peers:
        if peer not in self.peer_manager.list_peers():
          self.peer_manager.add_peer(peer)
      return discovered_peers
    except Exception as e:
      print(f"Peer discovery failed: {e}")

  async def stop(self):
    """
      Close all WebRTC conncections and stop the host.
    """
    for pc in self.peer_connections.values():
        await pc.close()
        print("Host stopped.")
    # else:
    #     print("Host was not initialized, skipping stop.")