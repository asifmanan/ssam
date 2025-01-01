class Peer:
    def __init__(self, host: str, port: str):
        self.host = host
        self.port = port

    def get_hostname(self):
        return self.host

    def get_port(self):
        return self.port
    
    def __eq__(self, other):
        return isinstance(other, Peer) and self.host == other.host and self.port == other.port

    def __hash__(self):
        return hash((self.host, self.port))

    def __str__(self):
        return f"{self.host}:{self.port}"