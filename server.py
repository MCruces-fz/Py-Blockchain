from hashlib import sha256
import json

class Block:
    def __init__(self, index, transactions, timestamp):
        self.index = [] 
        self.transactions = transactions 
        self.timestamp = timestamp

 
def compute_hash(block): 
    """ 
    Function to create hash from a block

    :param block: json object
    :return: sha256 string
    """ 
    block_string = json.dumps(block, sort_keys=True) 
    return sha256(block_string.encode()).hexdigest()
