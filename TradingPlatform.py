from Pyfhel import Pyfhel, PyPtxt, PyCtxt
import PlatformUser


class TradingPlatform:
    def __init__(self):
        self.encryption = Pyfhel()
        self.encryption.contextGen(p=65537)
        self.encryption.keyGen()
        self.userDict = {}

    def load_users(self, users):
        for user in users:
            self.userDict[user.name] = PlatformUser.PlatformUser(user.name, 0, user.encryption.to_bytes_context(),
                                                                 user.encryption.to_bytes_publicKey())
            print("loaded: " + str(self.userDict[user.name]))

    def execute_trade(self, name, committed_amount, real_amount, trading_price, tariff, imported):
        user = self.userDict[name]
        self.encryption.from_bytes_context(user.context)
        self.encryption.from_bytes_publicKey(user.public_key)
        user.bill = self.encryption.encryptFrac(0)
        # bill calculations are in a very weird order so that they work for Pyfhel's methods as they take the + and *
        # operators and call their own methods from those in which the first argument must be a Pyfhel object
        if imported:
            period_bill = (committed_amount * trading_price - ((real_amount - committed_amount) * -tariff))
            user.bill += period_bill
            return period_bill
        else:
            exported = self.encryption.negate(committed_amount)
            period_bill = (exported * trading_price - ((exported + real_amount) * tariff))
            user.bill += period_bill
            return period_bill
