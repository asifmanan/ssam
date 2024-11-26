import threading
import time

class Miner:
  def __init__(self, mining_instance, interval = 3):
    """
        Initializes the Miner with a Mining instance and an optional mining interval.
    """
    self.mining_instance = mining_instance
    self.interval = interval
    self.is_mining = False
    self.thread = None
    self.lock = threading.Lock()
    self.stop_event = threading.Event()

  def start_mining(self):
    """
        Starts the mining process in a separate thread.
    """
    with self.lock:
      if self.is_mining:
        print("Miner is already running on this node")
        return
      self.is_mining = True
      self.stop_event.clear()

    self.thread = threading.Thread(target=self._mine, daemon=True)
    self.thread.start()
    print("Miner has Started...")

  def _mine(self):
    """
        The mining loop that continues until mining is stopped.
    """
    try:
      while not self.stop_event.is_set():
        new_block = self.mining_instance.mine_block()
        print("New Block created: " + str(new_block.index))
        time.sleep(self.interval)

    except Exception as e: 
      print(f"An error occured while mining the block: {e}")
    finally:
      print("Mining loop exiting...")

  def stop_mining(self):
    """
        Stops the mining process.
    """
    with self.lock:
      if not self.is_mining:
        print("Miner is not running")
        return
      self.is_mining = False

    self.stop_event.set()

    if self.thread and self.thread.is_alive():
      print("Waiting for mining thread to stop...")
      while self.thread.is_alive():
        time.sleep(0.1) # Allow thread to exit gracefully 
      # Ensuring the mining thread exits before continuing
      # self.thread.join()
      print("Mining process Halted")
