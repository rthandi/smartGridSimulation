from Pyfhel import Pyfhel, PyPtxt, PyCtxt
import struct
from Cryptodome.PublicKey import RSA, ECC
from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.Signature import DSS
from Cryptodome.Hash import SHA256


class User:
    def __init__(self, trading_platform_rsa_key, name=None):
        self.name = name
        self.imported = 0
        self.exported = 0
        self.realTradeAmount = 0
        self.bid = 0
        self.bill = 0
        self.ecc_private_key = ECC.generate(curve='P-256')
        self.rsa_public_key_trading_platform = trading_platform_rsa_key

    def __str__(self):
        return "User: " + self.name + " bill: " + str(self.bill)

    def get_public_key(self):
        return self.ecc_private_key.public_key().export_key(**{"format": "DER"})

    def reset(self):
        self.imported = 0
        self.exported = 0
        self.realTradeAmount = 0
        self.bid = 0

    def execute_trade(self, committed_amount, real_amount, trading_price, tariff, imported):
        # bill calculations are in a very weird order so that they work for Pyfhel's methods as they take the + and *
        # operators and call their own methods from those in which the first argument must be a Pyfhel object
        if imported:
            period_bill = (committed_amount * trading_price - ((real_amount - committed_amount) * - tariff))
        else:
            exported = -committed_amount
            period_bill = (exported * trading_price - ((exported + real_amount) * tariff))

        self.bill += period_bill

        return period_bill

    def verify_send(self, trading_platform):
        # this is slightly hacky as hashing is not always a good idea for floats. This may work because it is a price
        # and therefore always rounds to 2 and the calculation is the same on both ends but there is a small chance
        # it could break (likely dependent on the inner workings of Pyfhel)
        hashed_bill = SHA256.new(struct.pack('<f', self.bill))

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

        trading_platform.verify_receive_user(self.name, enc_session_key, cipher_aes.nonce, tag, ciphertext, signature)

