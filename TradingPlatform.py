from Pyfhel import Pyfhel, PyPtxt, PyCtxt

class TradingPlatform:
    def __init__(self, key):
        self.encryption = Pyfhel()
        self.encryption.contextGen(p=65537)
        self.encryption.from_bytes_publicKey(key)
        self.user_dict = {}
        self.period_counter = 0

    def load_users(self, users):
        for user in users:
            self.user_dict[user.name] = self.encryption.encryptFrac(0)
            print("trading platform loaded: " + str(self.user_dict[user.name]))

    def execute_trade(self, name, committed_amount, real_amount, trading_price, tariff, imported, supplier, period_count):
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

        self.user_dict[name] += period_bill

        if (period_count + 1) % 24 == 0:
            supplier.update_bill(name, self.user_dict[name])
            self.user_dict[name] = self.encryption.encryptFrac(0)

        return period_bill
