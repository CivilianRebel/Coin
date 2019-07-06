"""
Created by Steven ODonnell on 6/29/2019
This class is the handler class for the blockchain.
All blocks are stored as JSON files in the naming
convention '{location}/blockchain/{key}.value'
containing the value
"""

import json
import os
import glob
import time
# imports from local package
from block import Block
from transaction import Transaction


class FileStore:

    def __init__(self, location='blockchain/', _subdir='blockchain/', **kwargs):
        self.buffer = kwargs.get('buffer_init', {})
        self.buffer_size = kwargs.get('buffer_size', 100)
        self._iteration_index = 0

        self.debug = kwargs.get('debug', False)
        self.location = location
        # check if the path is a folder not a file
        if self.location[-1] is not '/':
            self.location += '/'
        # if the path is not the default, add a subdir
        if self.location is not 'blockchain/':
            self.location = os.path.join(self.location, _subdir)

        if not os.path.exists(self.location):
            os.mkdir(self.location)
        self.size = len(glob.glob(self.value('*')))

    @staticmethod
    def exists(path):
        return os.path.exists(path)

    def value(self, key):
        if self.location[-1] is not '/':
            self.location += '/'
        return f'{self.location}{key}.value'

    def load_value(self, key):
        loaded_block = None
        if not self.exists(self.value(key)):
            raise KeyError('Key does not exist, handle this error.')
        with open(self.value(key), 'r') as data:
            json_file = json.load(data)
        if json_file:
            loaded_block = Block(json_file['block_id'],
                                 json_file['previous_block_hash'],
                                 list(json_file['transactions']),
                                 json_file['timestamp'],
                                 json_file['block_difficulty'],
                                 json_file['nonce'])
        return loaded_block

    @property
    def files(self):
        return glob.glob(self.value('*'))

    def append(self, value):
        if self.debug:
            print(f'{self.value(len(self))} created and "appended"')
        self[len(self)] = value

    def prealloc(self, ln=5000):
        for f in range(ln):
            with open(self.value(len(self)), 'w+') as p:
                p.write('0')

    def remove_all(self):
        if self.debug:
            print(f'Deleting all files in {self.location}')
        for path in self.files:
            os.remove(path)
            if self.debug:
                print(f'{path} removed')
        if self.debug:
            print('Removed files, trying to remove directory')
        self.size = 0
        self.size_update = 0
        os.rmdir(self.location)
        if self.debug:
            print(f'Deleted directory\n# of files in self.location: {len(self)}')
        if len(self) > 0:
            raise OSError
        os.mkdir(self.location)

    def __len__(self):
        return self.size

    def __next__(self):
        if len(self) > self._iteration_index:
            self._iteration_index += 1
            return [self[self._iteration_index - 1], self.value(self._iteration_index - 1)]
        else:
            self._iteration_index = 0
            raise StopIteration

    def __str__(self):
        return 'Printing list of key-files:\n' + str(self.files)

    def __setitem__(self, key, value):
        assert type(value) is Block, 'Tried to set a block on the chain that was not a Block() object'
        if not self.exists(self.value(key)):
            self.size += 1
        with open(self.value(key), 'w+') as data:
            json.dump(value.dict, data)

    def __getitem__(self, key):
        # TODO: add a cache buffer to increase write times
        # don't think this really matters because of total size of network rn
        # and the block won't come in fast enough to matter unless its an init download
        # TODO: add a flag for cache buffer to only enable on init blockchain download
        if type(key) is int:
            if int(key) is -1:
                key = len(self) - 1
        try:
            return self.load_value(str(key))
        except KeyError:
            print(f'Key did not exist, check your code man.')
            return None


class Blockchain:

    def __init__(self):
        self.transactions = []
        self.chain = FileStore()
        self.difficulty = 3

    def latest_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction: Transaction):
        # TODO: add handling for transaction verification and adding to list
        pass

    def add_block_to_chain(self, block: Block):
        # verify signature
        if self.chain[-1].hashed == block.previous_block_hash:
            # ok this falls in order
            if block.verify_nonce():
                # this block is good to go
                self.chain.append(block)
                return True
            return False
        return False


def init(n):
    chain = FileStore(debug=True, update_freq=7500)
    for i in range(n):
        chain.append(Block(f'b{i}', str(hash(i)), [f'{i}'*i], time.time()))
    return chain


if __name__ == '__main__':
    chain = init(500)
    print(len(chain))
    chain.remove_all()
    s = time.time()
    try:
        chain['1'] = 'test block assertiom'
    except:
        pass
    chain = init(25)
    print(time.time() - s)
