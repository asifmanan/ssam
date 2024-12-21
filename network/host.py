import logging
import asyncio
from config import load_config
from aiortc import RTCPeerConnection, RTCSessionDescription
from network.peer_discovery import PeerDiscovery
from network.peer_manager import PeerManager
from network.message_handler import MessageHandler
from network.utils import MuxAddressParser
from network.utils import InterfaceInfo
from network.message import Message

class Host:
  def __init__(self, config_path: str):
    # Load configuration
    config = load_config(config_path)

    self.bootstrap_nodes = config["peers"]
    listen_ip = InterfaceInfo.get_local_ip()

    listen_port = InterfaceInfo.get_port()
    self.listen_addr = f"{listen_ip}:{listen_port}"

    #  Initialize components
    self.peer_manager = PeerManager()
    self.peer_discovery = PeerDiscovery(listen_ip = listen_ip, 
                                        listen_port = listen_port,
                                        bootstrap_nodes_list = self.bootstrap_nodes)
    self.message_handler = MessageHandler(self)
    self.peer_connections = {} 

  async def start(self):
    """
      Start the host and begin peer discovery.
    """
    try:  
      await self.peer_discovery.start()
      await self.peer_discovery.announce_peer()
    except Exception as e:
      logging.error(f"Failed to start host: {e}")

  async def connect_to_peer(self, peer_addr: str) -> None:
    """
      Connect to a peer using its multiaddress.
    """
    async def connect_to_peer(self, peer_addr: str) -> None:
      try:
          pc = RTCPeerConnection()
          pc.dataChannels = {}  # Track data channels
          self.peer_connections[peer_addr] = pc

          # Create a data channel if one doesn't exist
          if "data_channel" not in pc.dataChannels:
              data_channel = pc.createDataChannel("data_channel")
              pc.dataChannels["data_channel"] = data_channel

              @data_channel.on("open")
              def on_open():
                  logging.info(f"Data channel with {peer_addr} is open.")

              @data_channel.on("message")
              def on_message(message):
                  logging.info(f"Received message from {peer_addr}: {message}")

          # Create and send offer
          offer = await pc.createOffer()
          await pc.setLocalDescription(offer)

          # Store signaling data in DHT
          await self.peer_discovery.store_signaling_data(peer_addr, {"type": "offer", "sdp": offer.sdp})
          logging.info(f"Offer sent to peer {peer_addr}")

          # Add peer to PeerManager
          self.peer_manager.add_peer(peer_addr, address=peer_addr, connection=pc)

      except Exception as e:
          logging.error(f"Failed to connect to {peer_addr}: {e}")

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
          logging.info(f"Received message from {peer_addr}: {message}")

      # Set the remote description using the received offer
      offer = RTCSessionDescription(sdp=offer, type="offer")
      await pc.setRemoteDescription(offer)

      # Create and send an answer
      answer = await pc.createAnswer()
      await pc.setLocalDescription(answer)

      # Use peer discovery (Kademlia DHT) to send the answer
      await self.peer_discovery.server.set(peer_addr, answer.sdp)
      logging.info(f"Answer sent to peer {peer_addr}")

    except Exception as e:
      logging.error(f"Failed to handle incoming offer from {peer_addr}: {e}")

  
  async def send_message(self, peer, message: Message, protocol: str=None) -> None:
    """
        Send a message to a peer using a specific protocol.
    """
    serialized_message = message.to_json()
    await self.message_handler.send_message(peer, serialized_message)
  
  async def broadcast_message(self, message: Message) -> None:
    """
      Broadcast a message to all connected peers.
    """
    if not self.peer_manager.list_peers():
        logging.info("No connected peers to broadcast to.")
        return
    for peer_id in self.peer_manager.list_peers():
      try:
        # Use the message handler object to send the message
        await self.message_handler.send_message(peer_id, message)
        logging.info(f"Message broadcasted to {peer_id}")
      except Exception as e:
        logging.error(f"Failed to broadcast message to {peer_id}: {e}")

  def set_stream_handler(self, protocol: str, handler) -> None:
    """
      Register a handle for incoming streams.
    """
    self.host.set_stream_handler(protocol, handler)
  
  async def start_peer_discovery(self, key: str = None, limit: int = 10):
    """
      Discover peers using DHT.
    """
    try:
      discovered_peers = await self.peer_discovery.discover_peers(limit=limit)
      for peer in discovered_peers:
        if peer["node_id"] not in self.peer_manager.list_peers():
          self.peer_manager.add_peer(peer["node_id"], peer["address"])
      return discovered_peers
    except Exception as e:
      logging.error(f"Peer discovery failed: {e}")

  async def stop(self):
    """
      Close all WebRTC conncections and stop the host.
    """
    for pc in self.peer_connections.values():
        await pc.close()
        logging.info("Host stopped.")