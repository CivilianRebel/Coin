import binascii
import json

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 as pkcs15


class Transaction:

    def __init__(self, sender_public, recipient_public, amount, timestamp, sig=False, sender_private=False):
        self.sender_public = sender_public
        self.recipient_public = recipient_public
        self.timestamp = timestamp
        self.amount = amount
        if sig is not False:
            self.signature = sig
        else:
            self.signature = None
        if sender_private is not False:
            self.sender_private = sender_private
        else:
            self.sender_private = None

    def sign(self):
        assert self.sender_private is not None, 'To use this function, please set the private key in the constructor'
        return self.sign_with_key(self.sender_private)

    def sign_with_key(self, private_key):
        pvk = RSA.importKey(binascii.unhexlify(private_key))
        signer = pkcs15.new(pvk)
        h = SHA256.new(str(self).encode('utf8'))
        self.signature = binascii.hexlify(signer.sign(h)).decode('ascii')
        return self.signature

    def generate_tx_string(self):
        # lazy json making lmao
        if self.signature is None:
            print(f'[WARNING]\t\tGenerating transaction string before it has been signed')
        ret_dict = {'sender_public': self.sender_public,
                    'recipient_public': self.recipient_public,
                    'amount': self.amount,
                    'time': self.timestamp,
                    'signature': self.signature}
        return json.dumps(ret_dict, sort_keys=True)

    @property
    def verified(self):
        """
        Returns boolean of if the transaction is A) signed AND B) The signature matches
        :return:
        """
        if self.signature is None:
            return False
        pubkey = RSA.importKey(binascii.unhexlify(self.sender_public))
        verifier = pkcs15.new(pubkey)
        _hash = SHA256.new(str(self).encode('utf8'))
        if verifier.verify(_hash, binascii.unhexlify(self.signature)):
            return True
        else:
            return False

    def __str__(self):
        return self.generate_tx_string()


if __name__ == '__main__':
    b = Transaction('public1', 'public2', 45.3, 101)
    print(b)