from Pyfhel import Pyfhel, PyPtxt, PyCtxt
from time import process_time


class TradingPlatform:
    def __init__(self, homo_key):
        self.encryption = Pyfhel()
        self.encryption.contextGen(p=65537)
        self.encryption.from_bytes_publicKey(homo_key)
        self.user_dict = {}
        self.period_counter = 0
        self.timeTally = 0

    def load_users(self, users):
        for user in users:
            self.user_dict[user.name] = {'name': user.name, 'bill': self.encryption.encryptFrac(0),
                                         'pub_key': user.get_public_key(), 'hashed_bill': None}
            print("trading platform loaded: " + str(self.user_dict[user.name]['name']))

    def execute_trade(self, name, committed_amount, real_amount, trading_price, tariff, imported, supplier,
                      period_count):

        # bill calculations are in a very weird order so that they work for Pyfhel's methods as they take the + and *
        # operators and call their own methods from those in which the first argument must be a Pyfhel object
        if imported:
            t1_start = process_time()
            period_bill = (committed_amount * trading_price - ((real_amount - committed_amount) * - tariff))
            t1_stop = process_time()
            self.timeTally += (t1_stop-t1_start)
        else:
            exported = self.encryption.negate(committed_amount)
            t1_start = process_time()
            period_bill = (exported * trading_price - ((exported + real_amount) * tariff))
            t1_stop = process_time()
            self.timeTally += (t1_stop-t1_start)

        self.user_dict[name]['bill'] += period_bill

        # trading period set to update bills once per month (48 * 30 due to there being a period every 30 minutes)
        if (period_count + 1) % (48*30) == 0:
            print(str(self.timeTally))
            supplier.update_bill(name, self.user_dict[name]['bill'])
            self.user_dict[name]['bill'] = self.encryption.encryptFrac(0)

        return period_bill
