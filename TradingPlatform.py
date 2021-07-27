from Pyfhel import Pyfhel, PyPtxt, PyCtxt
import PlatformUser


class TradingPlatform:
    def __init__(self, key):
        self.encryption = Pyfhel()
        self.encryption.contextGen(p=65537)
        self.encryption.from_bytes_publicKey(key)
        self.userDict = {}

    def load_users(self, users):
        for user in users:
            self.userDict[user.name] = self.encryption.encryptFrac(0)
            print("trading platform loaded: " + str(self.userDict[user.name]))

    def get_pub_key(self):
        return self.encryption.to_bytes_publicKey()

    def execute_trade(self, name, committed_amount, real_amount, trading_price, tariff, imported, supplier):
        # self.encryption.from_bytes_context(user.context)
        # committed_amount = self.encryption.decryptFrac(committed_amount)
        # real_amount = self.encryption.decryptFrac(real_amount)

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
            exported = self.encryption.negate(committed_amount)
            period_bill = (exported * trading_price - ((exported + real_amount) * tariff))
            self.userDict[name] += period_bill
            supplier.update_bill(name, period_bill)
            return period_bill
