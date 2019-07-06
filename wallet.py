"""
this file contains the wallet handler
"""
import os
import Crypto.Random
from Crypto.PublicKey import RSA
import binascii
import json


class Wallet:

    def __init__(self, loc='wallet.json'):
        self.save_location = loc
        self.wallet = {'public_key': None,
                       'private_key': None}

    @staticmethod
    def generate_new():
        random_gen = Crypto.Random.new().read
        private_key = RSA.generate(1024, random_gen)
        public_key = private_key.publickey()

        public_key = binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')
        private_key = binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii')
        return {'public_key': public_key, 'private_key': private_key}

    def load(self):
        if not os.path.exists(self.save_location):
            raise FileNotFoundError('Could not find wallet file, not handled here yet')
        else:
            with open(self.save_location, 'r') as file:
                self.wallet = json.load(file)

    def create(self):
        # TODO: add check to see if folder exists
        if os.path.exists(self.save_location):
            raise FileExistsError('File already exists, for right now this is not implemented')
        else:
            self.wallet = self.generate_new()
            with open(self.save_location, 'w+') as file:
                json.dump(self.wallet, file)
