from Pyfhel import Pyfhel, PyPtxt, PyCtxt
import cryptography
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import PlatformUser


class TradingPlatform:
    def __init__(self, key):
        self.homoEncryption = Pyfhel()
        self.homoEncryption.contextGen(p=65537)
        self.homoEncryption.from_bytes_publicKey(key)
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        self.userDict = {}

        serial_pub = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        with open('TradingPlatformPubKey.pem', 'wb') as f: f.write(serial_pub)

    def load_users(self, users):
        for user in users:
            self.userDict[user.name] = self.homoEncryption.encryptFrac(0)
            print("trading platform loaded: " + str(self.userDict[user.name]))

    def execute_trade(self, name, committed_amount, real_amount, trading_price, tariff, imported, supplier):
        # self.encryption.from_bytes_context(user.context)
        committed_amount = self.homoEncryption.decrypt(committed_amount.from_bytes())
        real_amount = self.homoEncryption.decrypt(real_amount.from_bytes())

        # bill calculations are in a very weird order so that they work for Pyfhel's methods as they take the + and *
        # operators and call their own methods from those in which the first argument must be a Pyfhel object
        print(real_amount)
        print(committed_amount)
        if imported:
            period_bill = (committed_amount * trading_price - ((real_amount - committed_amount) * - tariff))
            self.userDict[name] += period_bill
            supplier.update_bill(name, period_bill)
            return period_bill
        else:
            exported = self.homoEncryption.negate(committed_amount)
            period_bill = (exported * trading_price - ((exported + real_amount) * tariff))
            self.userDict[name] += period_bill
            supplier.update_bill(name, period_bill)
            return period_bill
