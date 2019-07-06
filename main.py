"""
Created by Steven ODonnell on 6/30/2019
This class implements the gui for the application
for now this is just a CLI
"""
import os
from blockchain import Blockchain
from network import Peer
from wallet import Wallet
from uuid import uuid4


class Main:

    def __init__(self):
        self.running = True
        self.blockchain = Blockchain()
        self.wallet = None
        self.id = str(uuid4()).replace('-', '')
        self.network = Peer(self.id, '127.0.0.1', 25565)
        self.handlers = {'1': self.load_wallet,
                         '2': self.create_wallet,
                         }

    def load_wallet(self):
        self.wallet = Wallet().load()

    def create_wallet(self):
        self.wallet = Wallet().create()

    def run(self):
        while self.running:
            # display options
            # gather input
            # process
            print('[1]\t\t Load wallet')
            print('[2]\t\t Create wallet')
            choice = input('Pick Number: ')
            os.system('cls')
            print(f'You chose {choice}')
            self.handlers[choice]()


if __name__ == '__main__':
    m = Main()
    m.run()
