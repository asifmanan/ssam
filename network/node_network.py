import asyncio
import signal
import logging
import platform
from network.host import Host
from config import load_config


class NodeNetwork:
  def __init__(self, config_path):
    """
    Initialize the NodeNetwork class.
    :param config_path: Path to the configuration file.
    """
    # Load the configuration file
    self.config = load_config(config_path)

    # Initialize the Host object
    self.host = Host(config_path)

    # Create a new event loop
    self.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(self.loop)

  async def start(self):
    """
    Start the NodeNetwork by initializing the host.
    """
    try:
        logging.info("Starting Network...")

        # Start the host 
        await self.host.start()

        # Discover peers using DHT
        logging.info("Discovering peers...")
        key = self.config.get("discovery_key", "default_key")
        discovered_peers = await self.host.discover_peers(key)
        logging.info(f"Discovered peers: {discovered_peers}")

        # Keep the node running
        logging.info("NodeNetwork is now running. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(10)

    except asyncio.CancelledError:
        logging.info("NodeNetwork shutting down...")
    except Exception as e:
        logging.error(f"Error in NodeNetwork: {e}")
        raise

  async def shutdown(self):
    """
    Gracefully shut down the NodeNetwork.
    """
    logging.info("Shutting down NodeNetwork...")

    # Cancel all running tasks
    tasks = [t for t in asyncio.all_tasks(self.loop) if not t.done()]
    for task in tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    logging.info("All tasks cancelled. NodeNetwork shut down cleanly.")

  def run(self):
    """
    Run the Network with platform-specific signal handling.
    """
    try:
      if platform.system() != "Windows":
          # Add signal handlers for Unix-like systems
          for sig in (signal.SIGINT, signal.SIGTERM):
              self.loop.add_signal_handler(sig, lambda: asyncio.ensure_future(self.shutdown()))
      else:
          logging.warning("Signal handlers are not supported on Windows. Use Ctrl+C to exit.")

      self.loop.run_until_complete(self.start())
    except KeyboardInterrupt:
      logging.info("KeyboardInterrupt received. Shutting down gracefully...")
      self.loop.run_until_complete(self.shutdown())
    finally:
      self.loop.close()


if __name__ == "__main__":
  # Configure logging
  logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

  # Specify the path to the configuration file
  config_path = "config.json"

  # Initialize and run the NodeNetwork
  node_network = NodeNetwork(config_path)
  node_network.run()
