from Pyfhel import Pyfhel, PyPtxt, PyCtxt
import struct
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Signature import pss
from Crypto.Hash import SHA256


class User:
    def __init__(self, supplier_homo_key, supplier_rsa_key, name=None):
        self.name = name
        self.imported = 0
        self.exported = 0
        self.realTradeAmount = 0
        self.bid = 0
        self.bill = 0
        self.encryption = Pyfhel()
        self.encryption.contextGen(p=65537)
        self.encryption.from_bytes_publicKey(supplier_homo_key)
        # self.ecc_private_key = ECC.generate(curve='P-256')
        self.rsa_private_key = RSA.generate(2048)
        self.rsa_public_key_supplier = supplier_rsa_key

    def __str__(self):
        return "User: " + self.name + " bill: " + str(self.bill)

    def get_public_key(self):
        return self.rsa_private_key.publickey().exportKey()

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

    def verify_send(self, supplier):
        # this is slightly hacky as hashing is not always a good idea for floats. This may work because it is a price
        # and therefore always rounds to 2 and the calculation is the same on both ends but there is a small chance
        # it could break (likely dependent on the inner workings of Pyfhel)
        hashed_bill = SHA256.new(struct.pack('<f', self.bill))

        # sign message
        user_key = self.rsa_private_key
        signature = pss.new(user_key).sign(hashed_bill)

        # encrypt message
        print(self.rsa_public_key_supplier)
        supplier_key = RSA.import_key(self.rsa_public_key_supplier)
        session_key = get_random_bytes(16)
        cipher_rsa = PKCS1_OAEP.new(supplier_key)
        enc_session_key = cipher_rsa.encrypt(session_key)

        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(hashed_bill.digest())

        supplier.verify_receive(self.name, enc_session_key, cipher_aes.nonce, tag, ciphertext, signature)

