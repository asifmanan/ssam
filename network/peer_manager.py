import os
import threading
from network.peer import Peer


class PeerManager:
    def __init__(self, peers_list: list):
        """
        Initialize the PeerManager with a list of peers.
        :params: peers_list (list): A list of peers in the format "host:port".
        """
        self.lock = threading.Lock()  # For thread-safe operations
        
        # Uncomment this line if not using with docker
        # hostname = socket.gethostname()
        
        # If using with docker, Get the node name from the environment, default to "node"
        node_name = os.environ.get("NODE_NAME", "node")
        
        self.this_peer = Peer(node_name, "5000")  # Determine own address
        self.peers = [Peer(*peer.split(":")) for peer in peers_list if peer != str(self.this_peer)]

    def add_peer(self, peer: Peer) -> bool:
        """
        Add a peer to the peer list if it doesn't already exist.

        :params: peer (Peer): The peer to add.

        :Returns: bool: True if the peer was added, False otherwise.
        """
        with self.lock:
            if peer not in self.peers and peer != self.this_peer:
                self.peers.append(peer)
                return True
            return False

    def remove_peer(self, peer: Peer) -> bool:
        """
        Remove a peer from the peer list.

        :params: peer (Peer): The peer to remove.
        :Returns: bool: True if the peer was removed, False otherwise.
        """
        with self.lock:
            if peer in self.peers:
                self.peers.remove(peer)
                return True
            return False

    def get_peers(self) -> list:
        """
        Get the list of peers.

        :Returns: list: List of Peer objects.
        """
        with self.lock:
            return list(self.peers)

    def find_peer(self, host: str, port: str) -> Peer:
        """
        Find a peer by host and port.

        :params: host (str): The host of the peer.
        :params: port (str): The port of the peer.
        :Returns: Peer: The matching Peer object, or None if not found.
        """
        with self.lock:
            for peer in self.peers:
                if peer.host == host and peer.port == port:
                    return peer
            return None

    def __str__(self):
        """
        Get a string representation of the peer list.
        """
        with self.lock:
            return ", ".join([str(peer) for peer in self.peers])