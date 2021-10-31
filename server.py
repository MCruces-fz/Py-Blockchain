from hashlib import sha256
import json
import time


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
        self.unconfirmed_transactions = [] # información para insertar en el blockchain
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

