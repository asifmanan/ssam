import logging 
import socket
from urllib.parse import urlparse
from kademlia.network import Server
from network.utils import MuxAddressParser
from network.utils import InterfaceInfo


class PeerDiscovery:
  def __init__(self, listen_port: int=None, bootstrap_nodes_list = None):
    """
    Initialize the PeerDiscovery class.

    :param bootstrap_nodes: A list of bootstrap nodes to start the DHT.
    """
    listen_ip = InterfaceInfo.get_local_ip()
    print(f"Host IP: {listen_ip}")

    if listen_port is None or not isinstance(listen_port, int):
      if not isinstance(listen_port, int):
        logging.error("Invalid listen port number, acquiring a random port.")
      listen_port = InterfaceInfo.get_port()
      print(f"Host Port: {listen_port}")

    if bootstrap_nodes_list is None:
      bootstrap_nodes_list = []

    self.bootstrap_nodes = self.validate_nodes(bootstrap_nodes_list)
    self.listen_port = listen_port
    self.listen_ip = listen_ip

    print(f"Bootstrap nodes: {self.bootstrap_nodes}")
    self.server = Server()

  def validate_nodes(self, bootstrap_nodes_list):
    """
    Validate the list of bootstrap nodes.

    :param nodes: The list of bootstrap nodes.
    :return: True if the nodes are valid, False otherwise.
    """
    valid_bootstrap_nodes = []
    if not isinstance(bootstrap_nodes_list, list):
      raise ValueError("Invalid bootstrap nodes list")
    
    for node in bootstrap_nodes_list:
      if isinstance(node, dict) and "addr" in node:
        addr = node["addr"]
      
        if addr:
          parsed = MuxAddressParser.parse(addr)
        
          if parsed:
            valid_bootstrap_nodes.append(parsed)
          else:
            raise ValueError(f"Invalid Multi-address format: {addr}")
        
        else:
          raise ValueError("Bootstrap node missing 'addr' field")
        
      else:
        raise ValueError(f"Unsupported bootstrap node type: {type(node)}. Expected a dictionary.")
      
    return valid_bootstrap_nodes


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