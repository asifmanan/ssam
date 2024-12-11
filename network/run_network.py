import asyncio
import logging
from network.host import Host


async def main():
    """
    Main function to test the networking functionality using the updated Host class.
    """
    # Configuration file path
    config_path = "config.json"

    # Initialize and start the host
    print("Initializing the host...")
    host = Host(config_path)
    await asyncio.sleep(3)

    print("Starting the host...")
    try:
        await host.start()
    except Exception as e:
        print(f"Failed to start the host: {e}")

    # Discover peers using a test key
    key = "test_key"
    print("Discovering peers...")
    discovered_peers = await host.start_peer_discovery(key)
    print(f"Discovered peers: {discovered_peers}")

    # Connect to the first discovered peer
    if discovered_peers:
        peer_addr = discovered_peers[0]
        print(f"Connecting to peer: {peer_addr}")
        await host.connect_to_peer(peer_addr)
        print(f"Connected to {peer_addr}")

        # Send a test message to the connected peer
        message = "Hello, Peer!"
        print(f"Sending message to {peer_addr}: {message}")
        await host.send_message(peer=peer_addr, protocol="data_channel", message=message)

    # Broadcast a message to all connected peers
    broadcast_message = "Broadcast message from host!"
    print(f"Broadcasting message: {broadcast_message}")
    await host.broadcast_message(broadcast_message)

    # Wait to ensure all messages are processed
    await asyncio.sleep(5)

    # Stop the host
    print("Stopping the host...")
    await host.stop()
    print("Test completed successfully.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
