import socket
import logging
class MuxAddressParser:
  @staticmethod
  def parse(address: str):
    """
    Parse the address into hostname and port.

    :param address: The address to parse.
    :return: A tuple containing the hostname and port.
    """
    
    parts = MuxAddressParser.validate_address(address)

    try:
      host = parts[2]
      protocol = parts[3]
      port = parts[4]

      # Handle IPv6 brackets for consistency
      if parts[1] == "ip6" and ":" in host:
        host = f"[{host}]"

      if protocol in ("tcp", "udp"):
        return host, int(port)
    except Exception as e:
      print(f"Error parsing address: {e}")
      return None

  @staticmethod
  def validate_address(address: str):
    """
    Validate the address format.

    :param address: The address to validate.
    :return: True if the address is valid, False otherwise.
    """
    parts = address.split("/")
    if len(parts) < 5 or parts[1] not in ("ip4", "ip6", "dns"):
      raise ValueError(f"Invalid address format {address}")
    return parts
  
  
  def parse_port(address: str):
    """
    Parse the port from the address.

    :param address: The address to parse.
    :return: The port number.
    """
    parts = MuxAddressParser.validate_address(address)
    port = int(parts[4])
    return port
  
class InterfaceInfo:
  @staticmethod
  def get_local_ip():
    """
    Get the local IP address of the host.

    :return: The local IP address.
    """
    try:
      with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("192.168.1.1",80))
        print("got the IP using the good method")
        return s.getsockname()[0]
    except Exception as e:
      print(f"Fallback to gethostbyname: {e}")
      try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
      except Exception as e2:
        print(f"Failed to determine IP: {e2}")
        # Fallback to localhost
        return "127.0.0.1"

  @staticmethod
  def get_port(default_port=5000):
    """
    Get a random port number.

    :return: A random port number.
    """
    try:
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", default_port))
        return s.getsockname()[1]
    except Exception as e:
      logging.error(f"Failed to bind port {default_port}: {e}")