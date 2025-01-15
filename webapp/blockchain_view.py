from flask import Flask, jsonify, render_template
import os

app = Flask(__name__, template_folder="templates")

# Placeholder for the blockchain object
blockchain = None
# Reference: https://flask.palletsprojects.com/en/2.0.x/quickstart/
@app.route('/')
def home():
    """
    Serve the main page of the blockchain viewer.
    """
    return render_template('index.html')

@app.route('/blocks', methods=['GET'])
def get_blocks():
    """
    Serve the list of all blocks in the blockchain.
    """
    if blockchain is None:
        return jsonify({"error": "Blockchain not initialized"}), 500

    # Convert the blockchain to a list of dictionaries
    blocks = [block.to_dict() for block in blockchain.chain]
    return jsonify(blocks)

def start_webserver(bc, node_name:str = None):
    """
    Start the Flask webserver with the given blockchain instance.

    :param bc: The blockchain instance to serve.
    """
    global blockchain
    blockchain = bc
    
    # for local uncomment the following for local
    # port = int(os.getenv("FLASK_PORT", 8000))
    
    # for docker uncomment the following dor docker
    port = 8000
    
    app.run(host="0.0.0.0", port=port, debug=False)