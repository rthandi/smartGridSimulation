from Pyfhel import Pyfhel, PyPtxt, PyCtxt

from Cryptodome.PublicKey import RSA, ECC
from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.Signature import DSS
from Cryptodome.Hash import SHA256


class TradingPlatform:
    def __init__(self, key):
        self.encryption = Pyfhel()
        self.encryption.contextGen(p=65537)
        self.encryption.from_bytes_publicKey(key)
        self.user_dict = {}
        self.period_counter = 0
        self.rsa_private_key = RSA.generate(2048)

    def get_rsa_pub_key(self):
        return self.rsa_private_key.publickey().exportKey()

    def load_users(self, users):
        for user in users:
            self.user_dict[user.name] = {'name': user.name, 'bill': self.encryption.encryptFrac(0),
                                         'pub_key': user.get_public_key(), 'hashed_bill': None}
            print("trading platform loaded: " + str(self.user_dict[user.name]['name']))

    def execute_trade(self, name, committed_amount, real_amount, trading_price, tariff, imported, supplier,
                      period_count):
        # self.encryption.from_bytes_context(user.context)
        # committed_amount = self.encryption.decryptFrac(committed_amount)
        # real_amount = self.encryption.decryptFrac(real_amount)

        # bill calculations are in a very weird order so that they work for Pyfhel's methods as they take the + and *
        # operators and call their own methods from those in which the first argument must be a Pyfhel object
        if imported:
            period_bill = (committed_amount * trading_price - ((real_amount - committed_amount) * - tariff))
        else:
            exported = self.encryption.negate(committed_amount)
            period_bill = (exported * trading_price - ((exported + real_amount) * tariff))

        self.user_dict[name]['bill'] += period_bill

        if (period_count + 1) % 24 == 0:
            supplier.update_bill(name, self.user_dict[name]['bill'])
            self.user_dict[name]['bill'] = self.encryption.encryptFrac(0)

        return period_bill

    def verify_receive_user(self, user_name, enc_session_key, nonce, tag, ciphertext, signature):
        user = self.user_dict[user_name]

        cipher_rsa = PKCS1_OAEP.new(self.rsa_private_key)
        session_key = cipher_rsa.decrypt(enc_session_key)

        # Decrypt the data with the AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        hashed_bill = cipher_aes.decrypt_and_verify(ciphertext, tag)
        sig_hash = SHA256.new(hashed_bill)

        user_pub_key = ECC.import_key(user['pub_key'])
        verifier = DSS.new(user_pub_key, 'fips-186-3')
        verifier.verify(sig_hash, signature)

        user['hashed_bill'] = hashed_bill
