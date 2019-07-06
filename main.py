"""
Created by Steven ODonnell on 6/30/2019
This class implements the gui for the application
for now this is just a CLI
"""
import time
from uuid import uuid4

from blockchain import Blockchain
from network import Peer
from transaction import Transaction
from wallet import Wallet


class Main:

    def __init__(self):
        self.running = True
        self.blockchain = Blockchain()
        self.wallet = None
        self.id = str(uuid4()).replace('-', '')
        self.network = Peer(self.id, '127.0.0.1', 25565)
        self.handlers = {'load': self.load_wallet,
                         'create': self.create_wallet,
                         'send': self.send
                         }

    def send(self):
        # TODO: clear screen
        print('\n'*20)
        to_addr = input('Recipient: ')
        amount = input('Amount: ')
        tx = Transaction(self.wallet.public_key,
                         to_addr,
                         amount,
                         time.time())
        print(f'Are you sure you want to send this transaction?')
        print(str(tx))
        confirm = input('Send? [y/n] ')
        signature = tx.sign_with_key(self.wallet.private_key)
        print('Transaction signed... posting to network')
        # self.peer_queue.put({'inv': str(tx))

    def load_wallet(self):
        self.wallet = Wallet().load()
        # self.blockchain.load_keys(self.wallet)
        print(f'Wallet loaded')

    def create_wallet(self):
        self.wallet = Wallet().create()
        # self.blockchain.load_keys(self.wallet)
        print(f'Wallet created')

    def run(self):
        while self.running:
            # display options
            # gather input
            # process
            if self.wallet is None:
                print('[load]\t\t Load wallet')
                print('[create]\t\t Create wallet')
            else:
                print('[send]\t\t Send coin to another address')
            choice = input('Pick Number: ')
            # os.system('cls')
            print(f'You chose [{choice}]')
            self.handlers[choice]()


if __name__ == '__main__':
    m = Main()
    m.run()
