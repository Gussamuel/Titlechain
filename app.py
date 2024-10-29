from flask import Flask, jsonify, request
from flask_cors import CORS
from blockchain import Blockchain, FormData  # Import Blockchain and FormData classes

# Initialize Flask app and enable CORS for frontend-backend communication
app = Flask(__name__)
CORS(app)
blockchain = Blockchain()  # Instantiate the blockchain

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """Add a new transaction and mine if enough transactions are available."""
    try:
        data = request.get_json()
        form_data = FormData(**data['form_data'])
        private_key = data['private_key']
        fee = data['fee']

        blockchain.new_transaction(form_data, private_key, fee)

        return jsonify({'message': 'Transaction added successfully'}), 201

    except Exception as e:
        print(f"Error adding transaction: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/mining-status', methods=['GET'])
def get_mining_status():
    return jsonify(blockchain.get_mining_status()), 200

@app.route('/transactions/pending', methods=['GET'])
def get_pending_transactions():
    """Retrieve the list of pending transactions."""
    try:
        transactions = [tx.to_dict() for tx in blockchain.current_transactions]
        return jsonify(transactions), 200

    except Exception as e:
        print(f"Error fetching pending transactions: {e}")
        return jsonify({'error': str(e)}), 400
    

@app.route('/mining-log', methods=['GET'])
def get_mining_log():
    """Retrieve the mining log."""
    try:
        return jsonify(blockchain.get_mining_log()), 200
    except Exception as e:
        print(f"Error fetching mining log: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/chain', methods=['GET'])
def full_chain():
    """Retrieve the full blockchain."""
    try:
        chain_data = [block.to_dict() for block in blockchain.chain]
        return jsonify({'length': len(chain_data), 'chain': chain_data}), 200

    except Exception as e:
        print(f"Error fetching blockchain: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/search', methods=['GET'])
def search():
    """Search for transactions by first or last name."""
    try:
        query = request.args.get('q').lower()
        results = []

        # Search through each block and transaction
        for block in blockchain.chain:
            for tx in block.transactions:
                if (query in tx.form_data.first_name.lower() or
                        query in tx.form_data.last_name.lower()):
                    results.append(tx.to_dict())

        return jsonify(results), 200

    except Exception as e:
        print(f"Error during search: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/fees', methods=['GET'])
def total_fees():
    """Retrieve the total fees collected so far."""
    try:
        return jsonify({'total_fees_collected': blockchain.total_fees_collected}), 200

    except Exception as e:
        print(f"Error fetching total fees: {e}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
