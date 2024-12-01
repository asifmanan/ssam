class PeerManager:
  def __init__(self):
    """
    Initialize the peer manager.
    Stores peer information using a dictionary.
    """
    self.peers = {}

  def add_peer(self, peer_id: str, connection=None, public_key=None):
    """
    Add a new peer to the peer manager.

    :param peer_id: The unique identifier of the peer.
    :param connection: RTCPeerConnection instance for WebRTC.
    :param public_key: The public key of the peer for cryptographic validation.
    """
    if peer_id not in self.peers:
      self.peers[peer_id] = {} 
    if connection:
      self.peers[peer_id]["connection"] = connection
    if public_key:
      self.peers[peer_id]["public_key"] = public_key

  def update_peer(self, peer_id: str, connection=None, public_key=None):
    """
    Update the information for an existing peer.

    :param peer_id: The unique identifier of the peer.
    :param connection: Updated RTCPeerConnection instance for WebRTC.
    :param public_key: TUpdated public key of the peer.
    """
    if peer_id in self.peers:
      print(f"Warning: Updating existing peer {peer_id}")
      if connection:
        self.peers[peer_id]["connection"] = connection
      if public_key:
        self.peers[peer_id]["public_key"] = public_key

  def remove_peer(self, peer_id: str):
    """
    Remove a peer from the peer manager.

    :param peer_id: The unique identifier of the peer to remove.
    """
    if peer_id in self.peers:
      del self.peers[peer_id]

  def get_peer_connection(self, peer_id: str):
    """
    Get the WebRTC connection for a specific peer.

    :param peer_id: The unique identifier of the peer.
    :return: The RTCPeerConnection instance for the peer (or None if not found).
    """
    return self.peers.get(peer_id, {}).get("connection", None)

  def get_peer_public_key(self, peer_id: str):
    """
    Get the public key of a specific peer.

    :param peer_id: The unique identifier of the peer.
    :return: The public key of the peer (or None if not found).
    """
    return self.peers.get(peer_id, {}).get("public_key", None)

  def list_peers(self):
    """
    List all peer IDs managed by the PeerManager.

    :return: A list of all peers IDs.
    """
    return list(self.peers.keys())