class Peer:
    def __init__(self, host: str, port: str):
        """
        Initialize a new peer object.
        :param host: The hostname of the peer.
        :param port: The port of the peer.
        """
        self.host = host
        self.port = port

    def get_hostname(self):
        """
        Get the hostname of the peer.
        """
        return self.host

    def get_port(self):
        """
        Get the port of the peer.
        """
        return self.port
    
    def __eq__(self, other):
        """
        Check if two peers are equal.
        """
        return isinstance(other, Peer) and self.host == other.host and self.port == other.port

    def __hash__(self):
        """
        Get a hash of the peer.
        """
        return hash((self.host, self.port))

    def __str__(self):
        """
        Get a string representation of the peer.
        """
        return f"{self.host}:{self.port}"