import asyncio
import threading
from blockchain.blockchain import Blockchain
from webapp.blockchain_view import start_webserver

async def main():
    # Initialize the blockchain
    blockchain = Blockchain()

    # Start Flask webserver in a daemon thread
    flask_thread = threading.Thread(target=start_webserver, args=(blockchain,), daemon=True)
    flask_thread.start()

    try:
        # Simulate adding blocks for testing
        while True:
            await asyncio.sleep(10)
            blockchain.add_block(blockchain.create_block(
                staker_signature="staker10_sig",
                tx_root="dummy_root"
            ))
            print("New block added!")
    except asyncio.CancelledError:
        print("Application shutdown requested.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Application stopped manually.")