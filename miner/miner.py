import threading
import time

class Miner:
  def __init__(self, mining_instance, interval = 5):
    """
        Initializes the Miner with a Mining instance and an optional mining interval.
    """
    self.mining_instance = mining_instance
    self.interval = interval
    self.is_mining = False
    self.thread = None

  def start_mining(self):
    """
        Starts the mining process in a separate thread.
    """
    if self.is_mining:
      print("Miner is already running on this node")
      return
    self.mining = True
    self.thread = threading.thread(target=self._mine)
    self.thread.start()
    print("Miner is running...")

  def _mine(self):
    """
        The mining loop that continues until mining is stopped.
    """
    while self.is_mining:
      response = self.mining_instance.mine_block()
      time.sleep(self.interval)

  def stop_mining(self):
    """
        Stops the mining process.
    """
    if not self.is_mining:
      return
    self.is_mining = False
    if self.thread:
      self.thread.join()
      print("Mining process Halted")
