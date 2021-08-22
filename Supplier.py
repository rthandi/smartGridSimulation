import struct

from Pyfhel import Pyfhel, PyPtxt, PyCtxt
from phe import paillier
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA, ECC
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.Signature import DSS


class Supplier:
    def __init__(self):
        self.paillier_public_key, self.paillier_private_key = paillier.generate_paillier_keypair()
        self.user_dict = {}
        self.rsa_private_key = RSA.generate(2048)

    def load_users(self, users):
        for user in users:
            self.user_dict[user.name] = {'name': user.name, 'bill': 0,
                                        'pub_key': user.get_public_key()}
            print("supplier loaded: " + str(self.user_dict[user.name]['name']))

    def get_paillier_public_key(self):
        return self.paillier_public_key

    def get_rsa_public_key(self):
        return self.rsa_private_key.publickey().exportKey()

    def get_user_bill_decrypted(self, user_name):
        return round(self.paillier_private_key.decrypt(self.user_dict[user_name]['bill']), 2)

    def update_bill(self, user_name, period_bill):
        self.user_dict[user_name]['bill'] += period_bill

    def print_bills(self):
        for user in self.user_dict:
            print("From Supplier: User: " + self.user_dict[user]['name'] + " bill: " +
                  str(round(self.paillier_private_key.decrypt(self.user_dict[user]['bill']), 2)))

    def verify_receive(self, user_name, enc_session_key, nonce, tag, ciphertext, signature):
        user = self.user_dict[user_name]

        cipher_rsa = PKCS1_OAEP.new(self.rsa_private_key)
        session_key = cipher_rsa.decrypt(enc_session_key)

        # Decrypt the data with the AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        hashed_bill_user = cipher_aes.decrypt_and_verify(ciphertext, tag)
        sig_hash = SHA256.new(hashed_bill_user)

        user_pub_key = ECC.import_key(user['pub_key'])
        verifier = DSS.new(user_pub_key, 'fips-186-3')
        verifier.verify(sig_hash, signature)

        hashed_bill_supplier = SHA256.new(struct.pack('<f', self.get_user_bill_decrypted(user_name)))

        if hashed_bill_user == hashed_bill_supplier.digest():
            print("Bills have been verified by the supplier")
        else:
            raise ValueError('Bills for user ' + user_name + ' are not matching!')



