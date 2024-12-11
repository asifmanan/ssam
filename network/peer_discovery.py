import logging 
from kademlia.network import Server
from network.utils import MuxAddressParser


class PeerDiscovery:
  def __init__(self, listen_ip: int=None, listen_port: int=None, bootstrap_nodes_list = None):
    """
    Initialize the PeerDiscovery class.

    :param bootstrap_nodes: A list of bootstrap nodes to start the DHT.
    """

    if bootstrap_nodes_list is None:
      bootstrap_nodes_list = []

    self.bootstrap_nodes = self.validate_nodes(bootstrap_nodes_list)
    self.listen_port = listen_port
    self.listen_ip = listen_ip
    self.server = Server()
    self.node_id = self.server.node.long_id
    self.address = f"{self.listen_ip}:{self.listen_port}"

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
      await self.server.listen(port = self.listen_port, interface = self.listen_ip)
      logging.info(f"Kademlia server started at {self.listen_ip}:{self.listen_port}")

      # Check for bootstrap nodes
      if not self.bootstrap_nodes:
        logging.info("No bootstrap nodes provided, Operating in standalone mode.")
        return
      
      logging.info(f"Starting PeerDiscovery and bootstrapping...")
      await self.server.bootstrap(self.bootstrap_nodes)
      print(f"Node ID: {self.node_id}")

      logging.info(f"PeerDiscovery started and bootstrapped.")
    except Exception as e:
      logging.error(f"Failed to start PeerDiscovery: {e}")

  async def announce_peer(self):
    """
    Announce this node's presence in the DHT using its node id as the key.
    """
    try:
      await self.server.set(self.node_id, self.address)
      logging.info(f"Announced peer {self.node_id} at {self.address}")
    except Exception as e:
      logging.error(f"Failed to announce peer {self.node_id}: {e}")
  
  async def discover_peers(self, limit: int = 10):
    """
     Discover peers by finding the closest nodes in the DHT to this node.

    :param limit: The maximum number of peers to return.
    :return: A list of discovered peers. 
    """
    try:
      
      closest_peers = self.server.protocol.router.find_neighbors(self.server.node, k=limit)

      if closest_peers:
        logging.info(f"Discovered peers: {closest_peers}")
        return [{"node_id": peer.long_id, "address": f"{peer.ip}:{peer.port}"} for peer in closest_peers]
      else:
        logging.info("No peers found.")
        return []
      
    except Exception as e:
      logging.error(f"Failed to discover peers: {e}")
      return []
    
  async def store_signaling_data(self, peer_id: str, signaling_data: dict):
    """
    Store signaling data (offer/answer) for a peer in the DHT.
    
    :param peer_id: The unique identifier of the peer.
    :param signaling_data: The signaling data to store (WebRTC offers/answers).
    """
    try:
      await self.server.set(peer_id, signaling_data)
      logging.info(f"Signaling data stored for peer {peer_id}")
    except Exception as e:
      logging.error(f"Failed to store signaling data for {peer_id}: {e}")

  async def get_signaling_data(self, peer_id: str):
    """
    Retreive signaling data (offer/answer) for a peer from the DHT.

    :param peer_id: The unique identifier of the peer.
    :return: The retreived signaling data (WebRTC offers/answers) for the peer (or None of not found).
    """
    try:
      signaling_data = await self.server.get(peer_id)
      if signaling_data:
        logging.info(f"Retrieved signaling data for peer {peer_id}")
        return signaling_data
      else:
        logging.info(f"No signaling data found for peer {peer_id}")
        return None
    except Exception as e:
      logging.error(f"Failed to get signaling data for {peer_id}: {e}")
      return None
    
  def validate_signaling_data(signaling_data):
    required_keys = {"type", "sdp"}
    return isinstance(signaling_data, dict) and required_keys.issubset(signaling_data.keys())