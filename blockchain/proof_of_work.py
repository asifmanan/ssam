class ProofOfWork:
  MAX_TARGET = MAX_TARGET = int("00000FFFF0000000000000000000000000000000000000000000000000000000", 16)
  MAX_NONCE = 2**32 - 1 # Limit the nonce to 32 bits (max 4,294,967,295)
  
  def find_valid_nonce(self, block):
    """
    Searches for a valid nonce that satisfies the proof of work.
    """
    target = self.nbits_to_target(block.nbits)
    while True:
      if block.nonce >= self.MAX_NONCE:
        return None
      computed_hash = block.compute_hash()
      if int(computed_hash, 16) < target:
        return block.nonce
      block.nonce += 1

  @staticmethod
  def target_to_nbits(target):
    """
    Converts a 256-bit target to the compact 'nbits' format.
    refs: https://en.bitcoin.it/wiki/Difficulty
          https://bitcoin.stackexchange.com/questions/30467/what-are-the-equations-to-convert-between-bits-and-difficulty
          https://stackoverflow.com/questions/22059359/trying-to-understand-nbits-value-from-stratum-protocol/22161019#22161019
    :param target: 256-bit target value
    """
    target_hex = f"{target:064x}"
    target_bytes = bytes.fromhex(target_hex)
    target_bytes = target_bytes.lstrip(b'\x00') # remove leading zeros
    exponent = len(target_bytes) # position of MBS
    coefficient = int.from_bytes(target_bytes[:3], byteorder='big')

    if coefficient >= 0x7FFFFF:
        coefficient >>= 8
        exponent += 1

    nbits = (exponent << 24) | coefficient
    return f"0x{nbits:08x}"
  
  @staticmethod
  def nbits_to_target(nbits):
    """
    Converts the compact `nBits` value back into the full 256-bit target.
    """
    if isinstance(nbits, str):
      nbits = int(nbits, 16)
    exponent = (nbits >> 24) & 0xFF
    coefficient = nbits & 0xFFFFFF

    target = coefficient * (256 ** (exponent - 3))
    return target
  
  @staticmethod
  def is_valid_proof(block, target):
    """
    Validates if the block hash is less than the target.
    """
    return int(block.compute_hash(), 16) < target