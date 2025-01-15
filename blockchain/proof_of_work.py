class ProofOfWork:
  """
  The Proof of Work algorithm for mining blocks.
  refs:   https://en.bitcoin.it/wiki/Difficulty
          https://bitcoin.stackexchange.com/questions/30467/what-are-the-equations-to-convert-between-bits-and-difficulty
          https://stackoverflow.com/questions/22059359/trying-to-understand-nbits-value-from-stratum-protocol/22161019#22161019
  """
  MAX_TARGET = int("0000FFFF00000000000000000000000000000000000000000000000000000000", 16)
  MAX_NONCE_VALUE = 2**32 - 1 # Limit the nonce to 32 bits (max 4,294,967,295)
  def __init__(self, nbits:str=None, target:str=None):
    """
    Initializes the Proof of Work.
    :param nbits: The compact 'nbits' format for the target.
    :param target: The 256-bit target value.
    """
    if target:
      new_target = int(target,16)
      self.current_target = new_target
    
    elif nbits:
      new_target = self.nbits_to_target(nbits)
      self.current_target = new_target

    else:
      self.current_target = self.MAX_TARGET
    
    self.max_nonce = self.MAX_NONCE_VALUE
  

  def find_valid_nonce(self, block):
    """
    Searches for a valid nonce that satisfies the proof of work.
    :param block: The block to be mined.
    """
    target = self.current_target
    while True:
      if block.nonce >= self.max_nonce:
        return None
      computed_hash = block.compute_hash()
      if int(computed_hash, 16) < target:
        return block.nonce
      block.nonce += 1

  def get_current_target(self):
    """
    Returns the current target value.
    """
    return self.current_target
  
  def get_current_target_nbits(self):
    """
    Returns the compact 'nbits' format for the current target.
    """
    return self.target_to_nbits(self.current_target)
  def get_current_target_hex(self):
    """
    Returns the current target value in hexadecimal.
    """
    return f"{self.current_target:064x}"

  @staticmethod
  def target_to_nbits(target):
    """
    Converts a 256-bit target to the compact 'nbits' format.
    :param target: 256-bit target value
    """
    target_hex = f"{target:064x}" # Pad with zeros to ensure 64 characters
    target_bytes = bytes.fromhex(target_hex) # Convert to bytes
    target_bytes = target_bytes.lstrip(b'\x00') # remove leading zeros
    exponent = len(target_bytes) # position of MSB
    coefficient = int.from_bytes(target_bytes[:3], byteorder='big')

    # Adjust the coefficient if it exceeds 24 bits (i.e., is >= 0x7FFFFF)
    if coefficient >= 0x7FFFFF: 
        coefficient >>= 8
        exponent += 1

    # Combine the exponent and coefficient into the compact nBits format
    nbits = (exponent << 24) | coefficient

    # Return the nBits value as a hexadecimal string formatted into 8 characters hexadecimal string
    return f"0x{nbits:08x}"
  
  @staticmethod
  def nbits_to_target(nbits):
    """
    Converts the compact `nBits` value back into the full 256-bit target.
    :param nbits: The compact 'nbits' format for the target.
    """
    if isinstance(nbits, str):
      nbits = int(nbits, 16)
    exponent = (nbits >> 24) & 0xFF # Shift right 24 bits and mask with 0xFF (8 bits)
    coefficient = nbits & 0xFFFFFF # Mask with 0xFFFFFF to get the last 24 bits

    target = coefficient * (256 ** (exponent - 3)) # Compute the full 256-bit target
    return target
  
  @staticmethod
  def is_valid_proof(block, target):
    """
    Validates if the block hash is less than the target.
    :param block: The block to be validated.
    """
    return int(block.compute_hash(), 16) < target