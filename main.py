"""
Created by Steven ODonnell on 6/30/2019
This class implements the gui for the application
for now this is just a CLI
"""
import os

class Main:

    def __init__(self):
        self.running = True

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


if __name__ == '__main__':
    m = Main()
    m.run()