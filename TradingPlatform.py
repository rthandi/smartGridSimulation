from Pyfhel import Pyfhel, PyPtxt, PyCtxt
from phe import paillier
from time import process_time


class TradingPlatform:
    def __init__(self):
        self.user_dict = {}
        self.period_counter = 0
        self.timeTally = 0

    def load_users(self, users):
        for user in users:
            self.user_dict[user.name] = {'name': user.name, 'bill': 0,
                                         'pub_key': user.get_public_key(), 'hashed_bill': None}
            print("trading platform loaded: " + str(self.user_dict[user.name]['name']))

    def execute_trade(self, name, committed_amount, real_amount, trading_price, tariff, imported, supplier,
                      period_count):
        print("trading. period count: " + str(period_count))

        # bill calculations are in a very weird order so that they work for Pyfhel's methods as they take the + and *
        # operators and call their own methods from those in which the first argument must be a Pyfhel object
        if imported:
            period_bill = (committed_amount * trading_price - ((real_amount - committed_amount) * (tariff * -1)))
        else:
            exported = committed_amount * -1
            period_bill = (exported * trading_price - ((exported + real_amount) * tariff))

        self.user_dict[name]['bill'] += period_bill

        # trading period set to update bills once per month (48 * 30 due to there being a period every 30 minutes)
        if (period_count + 1) % (30) == 0:
            supplier.update_bill(name, self.user_dict[name]['bill'])
            self.user_dict[name]['bill'] = 0

        return period_bill
