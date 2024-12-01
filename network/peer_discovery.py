import logging 
from urllib.parse import urlparse
from kademlia.network import Server
from network.utils import MuxAddressParser


class PeerDiscovery:
  def __init__(self, listen_port: int, bootstrap_nodes = None):
    """
    Initialize the PeerDiscovery class.

    :param bootstrap_nodes: A list of bootstrap nodes to start the DHT.
    """
    if bootstrap_nodes is None:
      bootstrap_nodes = []
    if not isinstance(bootstrap_nodes, list):
      raise ValueError("Invalid bootstrap nodes list")
    
    if not isinstance(listen_port, int):
      raise ValueError("Invalid port number")
    
    self.bootstrap_nodes = []
    self.listen_port = listen_port

    for node in bootstrap_nodes:
      if isinstance(node, dict) and "addr" in node:
        addr = node["addr"]
      
        if addr:
          parsed = MuxAddressParser.parse(addr)
        
          if parsed:
            self.bootstrap_nodes.append(parsed)
          else:
            raise ValueError(f"Invalid Multi-address format: {addr}")
        
        else:
          raise ValueError("Bootstrap node missing 'addr' field")
        
      else:
        raise ValueError(f"Unsupported bootstrap node type: {type(node)}. Expected a dictionary.")

    print(f"Bootstrap nodes: {self.bootstrap_nodes}")
    self.server = Server()

  async def start(self):
    """
    Start the kademlia server and bootstrap the network.
    """
    try: 
      await self.server.listen(self.listen_port)

      # Check for bootstrap nodes
      if not self.bootstrap_nodes:
        print("No bootstrap nodes provided, Operating in standalone mode.")
        return
      
      print("Starting PeerDiscovery and bootstrapping...")
      await self.server.bootstrap(self.bootstrap_nodes)
      print("PeerDiscovery started and bootstrapped.")
    except Exception as e:
      print(f"Failed to start PeerDiscovery: {e}")
      # logging.error(f"Failed to start PeerDiscovery: {e}")

  async def discover_peers(self, key: str, limit: int = 10):
    """
    Discover peers using DHT.

    :param key: The key to search for in the DHT.
    :param limit: The maximum number of peers to return.
    :return: A list of discovered peers with metadata.
    """
    try:
      peers = await self.server.get(key)
      if peers:
        print(f"Discovered peers: {peers}")
        # logging.info(f"Discovered peers: {peers}")
        # Retreive metadata for each peer (e.g. address, peer_id)
        return peers[:limit]
      else:
        print("No peers found.")
        # logging.info("No peers found.")
        return []
      
    except Exception as e:
      print(f"Failed to discover peers: {e}")
      # logging.error(f"Failed to discover peers: {e}")
      return []
    
  async def store_signaling_data(self, peer_id: str, signaling_data: dict):
    """
    Store signaling data (offer/answer) for a peer in the DHT.
    
    :param peer_id: The unique identifier of the peer.
    :param signaling_data: The signaling data to store (WebRTC offers/answers).
    """
    try:
      await self.server.set(peer_id, signaling_data)
      print(f"Signaling data stored for peer {peer_id}")
      # logging.info(f"Signaling data stored for peer {peer_id}")
    except Exception as e:
      print(f"Failed to store signaling data for {peer_id}: {e}")
      # logging.error(f"Failed to store signaling data for {peer_id}: {e}")

  async def get_signaling_data(self, peer_id: str):
    """
    Retreive signaling data (offer/answer) for a peer from the DHT.

    :param peer_id: The unique identifier of the peer.
    :return: The retreived signaling data (WebRTC offers/answers) for the peer (or None of not found).
    """
    try:
      signaling_data = await self.server.get(peer_id)
      if signaling_data:
        print(f"Retrieved signaling data for peer {peer_id}")
        # logging.info(f"Retrieved signaling data for peer {peer_id}")
        return signaling_data
      else:
        print(f"No signaling data found for peer {peer_id}")
        # logging.info(f"No signaling data found for peer {peer_id}")
        return None
    except Exception as e:
      print(f"Failed to retreive signaling data for {peer_id}: {e}")
      # logging.error(f"Failed to get signaling data for {peer_id}: {e}")
      return None
    
  def validate_signaling_data(signaling_data):
    required_keys = {"type", "sdp"}
    return isinstance(signaling_data, dict) and required_keys.issubset(signaling_data.keys())