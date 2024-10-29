# backend/miner.py

import requests
import time

BACKEND_URL = "http://localhost:5000"  # URL of the Flask backend

def fetch_transactions():
    """Fetch pending transactions from the backend."""
    try:
        response = requests.get(f"{BACKEND_URL}/chain")
        if response.status_code == 200:
            chain_data = response.json()
            return chain_data['chain'][-1]  # Get the last block
        else:
            print("Failed to fetch transactions")
            return None
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return None

def mine_block():
    """Mine a new block by solving the proof-of-work puzzle."""
    last_block = fetch_transactions()
    if not last_block:
        print("No transactions to mine.")
        return

    print("Mining block...")
    new_block = {
        'index': last_block['index'] + 1,
        'transactions': last_block['transactions'],
        'previous_hash': last_block['hash'],
        'nonce': 0,
    }

    # Simple proof-of-work puzzle: find a hash with leading zeros
    while not new_block.get('hash', '').startswith('0000'):
        new_block['nonce'] += 1
        block_string = str(new_block).encode()
        new_block['hash'] = requests.utils.quote(str(hash(block_string)))

    print(f"Block mined with nonce: {new_block['nonce']}")
    print(f"Hash: {new_block['hash']}")

    # Submit the mined block back to the network
    submit_block(new_block)

def submit_block(block):
    """Submit a newly mined block to the backend."""
    try:
        response = requests.post(f"{BACKEND_URL}/mine", json=block)
        if response.status_code == 200:
            print("Block successfully mined and submitted.")
        else:
            print(f"Failed to submit block: {response.status_code}")
    except Exception as e:
        print(f"Error submitting block: {e}")

if __name__ == "__main__":
    while True:
        mine_block()
        print("Waiting 30 seconds before next mining attempt...")
        time.sleep(30)  # Wait before mining the next block
