import struct

from Cryptodome.PublicKey import RSA, ECC
from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.Signature import DSS
from Cryptodome.Hash import SHA256


# Home Energy Management System
class HEMS:
    def __init__(self, name, supplier_rsa_key):
        self.name = name
        self.bill = 0
        self.ecc_private_key = ECC.generate(curve='P-256')
        self.rsa_public_key_supplier = supplier_rsa_key

    def get_public_key(self):
        return self.ecc_private_key.public_key().export_key(**{"format": "DER"})

    def execute_trade(self, committed_amount, real_amount, trading_price, tariff, imported):
        if imported:
            period_bill = (committed_amount * trading_price - ((real_amount - committed_amount) * (tariff * -1)))
        else:
            exported = -committed_amount
            period_bill = (exported * trading_price - ((exported + real_amount) * tariff))

        self.bill += period_bill

        return period_bill

    def get_bill(self):
        return round(self.bill, 2)

    def     verify_send(self, supplier):
        # this is slightly hacky as hashing is not always a good idea for floats. This may work because it is a price
        # and therefore always rounds to 2 and the calculation is the same on both ends
        hashed_bill = SHA256.new(struct.pack('<f', self.get_bill()))

        # sign message
        ecc_key = self.ecc_private_key
        signer = DSS.new(ecc_key, 'fips-186-3')
        sig_hash = SHA256.new(hashed_bill.digest())
        signature = signer.sign(sig_hash)

        # encrypt message
        platform_key = RSA.import_key(self.rsa_public_key_supplier)
        session_key = get_random_bytes(16)
        cipher_rsa = PKCS1_OAEP.new(platform_key)
        enc_session_key = cipher_rsa.encrypt(session_key)

        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(hashed_bill.digest())

        supplier.verify_receive(self.name, enc_session_key, cipher_aes.nonce, tag, ciphertext, signature)
