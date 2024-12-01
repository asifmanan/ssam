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
