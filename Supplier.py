import struct

from Pyfhel import Pyfhel, PyPtxt, PyCtxt
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA, ECC
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.Signature import DSS
from Cryptodome.Random import get_random_bytes


class Supplier:
    def __init__(self):
        self.encryption = Pyfhel()
        self.encryption.contextGen(p=65537)
        self.encryption.keyGen()
        self.user_dict = {}
        self.rsa_private_key = RSA.generate(2048)
        self.ecc_private_key = ECC.generate(curve='P-256')
        self.rsa_public_key_trading_platform = None

    def load_users(self, users):
        for user in users:
            self.user_dict[user.name] = {'name': user.name, 'bill': self.encryption.encryptFrac(0),
                                        'pub_key': user.get_public_key()}
            print("supplier loaded: " + str(self.user_dict[user.name]['name']))

    def load_trading_platform_key(self, key):
        self.rsa_public_key_trading_platform = key

    def get_homo_pub_key(self):
        return self.encryption.to_bytes_publicKey()

    def get_user_bill_decrypted(self, user_name):
        return round(self.encryption.decryptFrac(self.user_dict[user_name]['bill']), 2)

    def get_ecc_public_key(self):
        return self.ecc_private_key.public_key().export_key(**{"format": "DER"})

    def update_bill(self, user_name, period_bill):
        self.user_dict[user_name]['bill'] += period_bill

    def print_bills(self):
        for user in self.user_dict:
            print("From Supplier: User: " + self.user_dict[user]['name'] + " bill: " +
                  str(round(self.encryption.decryptFrac(self.user_dict[user]['bill']), 2)))

    def verify_send(self, user_name, trading_platform):
        # this is slightly hacky as hashing is not always a good idea for floats. This may work because it is a price
        # and therefore always rounds to 2 and the calculation is the same on both ends but there is a small chance
        # it could break (likely dependent on the inner workings of Pyfhel)
        hashed_bill = SHA256.new(struct.pack('<f', self.get_user_bill_decrypted(user_name)))

        # sign message
        ecc_key = self.ecc_private_key
        signer = DSS.new(ecc_key, 'fips-186-3')
        sig_hash = SHA256.new(hashed_bill.digest())
        signature = signer.sign(sig_hash)

        # TODO: maybe change this to this https://github.com/ecies/py
        # encrypt message
        platform_key = RSA.import_key(self.rsa_public_key_trading_platform)
        session_key = get_random_bytes(16)
        cipher_rsa = PKCS1_OAEP.new(platform_key)
        enc_session_key = cipher_rsa.encrypt(session_key)

        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(hashed_bill.digest())

        trading_platform.verify_receive_supplier(user_name, enc_session_key, cipher_aes.nonce, tag, ciphertext,
                                                 signature)




