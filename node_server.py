from hashlib import sha256
import json
import time

from flask import Flask, request
import requests


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self):
        """ 
        Function to create hash from a block

        :param block: json object
        :return: sha256 string
        """ 

        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class Blockchain:
    difficulty = 2
 
    def __init__(self):
        """
        Initialize Blockchain with a genesis block
        """
        self.unconfirmed_transactions = []
        self.chain = []
        self.create_genesis_block()
 
    def create_genesis_block(self):
        """
        Function to generate the genesis block and add it to the 
        chain. That block has index  0, previous hash 0 and a 
        valid hash.
        """

        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)
 
    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, block):
        """
        Tries distinct nonce values until get a hash that satisfies our
        difficulty criteria.
        """

        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    def add_block(self, block, proof):
        """
        Add block to chain after verification.
        """

        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not self.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)

        return True

    def is_valid_proof(self, block, block_hash):
        """
        Check if block_hash is a valid hash and satisfies our
        difficulty criteria.
        """

        return (block.hash.startswith('0' * Blockchain.difficulty) and 
                block.hash == block.compute_hash())

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def mine(self):
        """
        Interface to add transactions to blocks, put them in the 
        blockchain and calculate the proof of work.
        """

        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block

        new_block = Block(
                index=last_block.index + 1,
                transactions=self.unconfirmed_transactions,
                timestamp=time.time(),
                previous_hash=last_block.hash
                )

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []

        return new_block.index


app = Flask(__name__)

# the node's copy of blockchain
blockchain = Blockchain()

@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ["author", "content"]
    
    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404

    tx_data["timestamp"] = time.time()

    blockchain.add_new_transaction(tx_data)

    return "Success", 201

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data})

@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    return f"Block #{result} is mined."

# acecss point to get not confirmed transactions
@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)

peers = set()

# endpoint to add new peers to the network.
@app.route('/add_nodes', methods=['POST'])
def register_new_peers():
    nodes = request.get_json()
    if not nodes:
        return "Invalid data", 400
    for node in nodes:
        peers.add(node)

    return "Success", 201

app.run(debug=True, port=8000)
