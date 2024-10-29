import hashlib
import time
import json
import requests
from typing import List, Set
from ecdsa import SigningKey, NIST384p

class FormData:
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    def to_dict(self):
        """Convert the form data to a dictionary."""
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
        }

class Transaction:
    def __init__(self, form_data, private_key, fee):
        self.form_data = form_data
        self.fee = fee
        self.signature = self.sign_transaction(private_key)

    def sign_transaction(self, private_key):
        try:
            # Convert the private key from hex to bytes
            sk = SigningKey.from_string(bytes.fromhex(private_key), curve=NIST384p)
            # Generate the signature for the form data
            signature = sk.sign(repr(self.form_data).encode())
            return signature.hex()  # Return the signature as hex
        except Exception as e:
            print(f"Error during signing: {e}")
            raise e

    def to_dict(self):
        """Convert the transaction to a dictionary."""
        return {
            "form_data": self.form_data.to_dict(),
            "fee": self.fee,
            "signature": self.signature,
        }

class Block:
    def __init__(self, index, transactions, previous_hash, difficulty):
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = time.time()
        self.nonce = 0
        self.difficulty = difficulty
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True, default=str).encode()
        return hashlib.sha256(block_string).hexdigest()

    def to_dict(self):
        """Convert the block to a serializable dictionary."""
        return {
            "index": self.index,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "difficulty": self.difficulty,
            "hash": self.hash,
        }

class Blockchain:
    def __init__(self, difficulty=4):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        self.difficulty = difficulty
        self.admin_wallet = "admin_wallet_address"
        self.total_fees_collected = 0
        self.mining_log = []  # New: Track mining events
        self.mining_status = {"status": "Idle", "attempts": 0, "current_hash": ""}
        self.create_genesis_block()

    def create_genesis_block(self):
        valid_private_key = (
            "acfb5657e6b35f266fb3df6ee7e2a844618d7f4afaf31cd17934f31710ff96c3d548bfe2399041d339724034e894d772"
        )
        genesis_form = FormData("Genesis", "Block")
        genesis_transaction = Transaction(genesis_form, valid_private_key, 0)
        genesis_block = Block(0, [genesis_transaction], "0" * 64, self.difficulty)
        self.chain.append(genesis_block)
        self.log_mining_event("Genesis block mined.")

    def new_transaction(self, form_data, private_key, fee):
        """Add a new transaction to the list of pending transactions."""
        transaction = Transaction(form_data, private_key, fee)
        self.current_transactions.append(transaction)

        # Mine a block if we have 2 pending transactions
        if len(self.current_transactions) >= 2:
            self.mine()

    def mine(self):
        self.mining_status["status"] = "Mining in progress"
        last_block = self.chain[-1]
        index = last_block.index + 1
        previous_hash = last_block.hash
        transactions = self.current_transactions[:2]
        block = Block(index, transactions, previous_hash, self.difficulty)

        # Try different nonces until the hash meets the difficulty requirement
        while not block.hash.startswith("0" * self.difficulty):
            block.nonce += 1
            block.hash = block.compute_hash()

            # Update the mining status for real-time monitoring
            self.mining_status["attempts"] = block.nonce
            self.mining_status["current_hash"] = block.hash

        self.chain.append(block)
        self.log_mining_event(f"Block {block.index} mined: {block.hash}")
        self.current_transactions = self.current_transactions[2:]  # Clear mined transactions
        self.mining_status["status"] = "Idle"

    def log_mining_event(self, message):
        """Log mining events for debugging and monitoring."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.mining_log.append(f"[{timestamp}] {message}")

    def get_mining_status(self):
        """Return the current mining status."""
        return self.mining_status

    def get_mining_log(self):
        """Return the mining log."""
        return self.mining_log

    def add_block(self, block):
        """Add a new block to the blockchain after validation."""
        if self.is_valid_block(block, self.get_last_block()):
            self.collect_fees(block)
            self.chain.append(block)
            return True
        return False

    def collect_fees(self, block):
        """Collect fees from a block and add them to the admin wallet."""
        total_fees = sum(tx.fee for tx in block.transactions)
        self.total_fees_collected += total_fees

    def is_valid_block(self, block, previous_block):
        """Check if a block is valid."""
        return (
            block.previous_hash == previous_block.hash and
            block.hash[:self.difficulty] == '0' * self.difficulty and
            block.hash == block.compute_hash()
        )

    def get_last_block(self):
        """Get the latest block in the blockchain."""
        return self.chain[-1]

    def register_node(self, address):
        """Register a new node with the network."""
        self.nodes.add(address)

    def resolve_conflicts(self):
        """Resolve conflicts by replacing the chain with the longest valid one."""
        longest_chain = None
        max_length = len(self.chain)

        for node in self.nodes:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_valid_chain(chain):
                    max_length = length
                    longest_chain = chain

        if longest_chain:
            self.chain = longest_chain
            return True
        return False

    def is_valid_chain(self, chain):
        """Check if a given blockchain is valid."""
        for i in range(1, len(chain)):
            if not self.is_valid_block(chain[i], chain[i - 1]):
                return False
        return True
    def get_mining_job(self):
        """Provide a mining job to the external miner."""
        if len(self.current_transactions) < 2:
            return None  # No block to mine yet

        last_block = self.chain[-1]
        transactions = self.current_transactions[:2]
        return {
            "index": last_block.index + 1,
            "transactions": [tx.to_dict() for tx in transactions],
            "previous_hash": last_block.hash,
            "difficulty": self.difficulty,
        }

    def add_mined_block(self, block_data):
        """Receive mined block data from external miner."""
        block = Block(**block_data)
        if self.is_valid_block(block, self.chain[-1]):
            self.chain.append(block)
            self.current_transactions = self.current_transactions[2:]
            self.log_mining_event(f"Block {block.index} mined: {block.hash}")
            return True
        return False
