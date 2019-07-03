import json
from collections import OrderedDict
from hashlib import sha256


class Block:

    def __init__(self, block_id, previous_block_hash, transactions, timestamp, diff, nonce=None):
        self.block_id = block_id
        self.previous_block_hash = previous_block_hash
        self.transactions = transactions
        self.timestamp = timestamp
        self.nonce = self.nonce
        self.block_difficulty = diff

    def generate_block_string(self):
        # lazy json making lmao
        return json.dumps(self.dict)

    @property
    def hashed(self):
        return sha256(self.generate_block_string().encode('uft8')).hexdigest()

    def verify_nonce(self):
        return self.hashed[:]

    @property
    def dict(self):
        d = OrderedDict({'block_id': self.block_id,
                         'previous_block_hash': self.previous_block_hash,
                         'transactions': self.transactions,
                         'timestamp': self.timestamp,
                         'nonce': self.nonce})
        return d

    def __str__(self):
        return self.generate_block_string()


if __name__ == '__main__':
    b = Block('blockid', 'hash', ['tx'], 101)
    print(b)