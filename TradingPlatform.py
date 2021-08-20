from Pyfhel import Pyfhel, PyPtxt, PyCtxt
from time import process_time


class TradingPlatform:
    def __init__(self, homo_key):
        self.encryption = Pyfhel()
        self.encryption.from_bytes_publicKey(homo_key)
        self.encryption.contextGen(65537)
        self.user_dict = {}
        self.period_counter = 0
        self.timeTally = 0
        self.relinKeySize = 5


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
            neg_tariff = self.encryption.negate(tariff, True)
            # hello = ((real_amount - committed_amount) * neg_tariff)
            # supplier.decrypt_val(real_amount)
            # supplier.decrypt_val(committed_amount)
            period_bill = (committed_amount * trading_price - ((real_amount - committed_amount) * neg_tariff))
            t1_stop = process_time()
            self.timeTally += (t1_stop-t1_start)
        else:
            exported = self.encryption.negate(committed_amount, True)
            # supplier.decrypt_val(committed_amount)

            # print("vals:")
            # supplier.decrypt_val(tariff)
            # hello = exported + real_amount
            # supplier.decrypt_val(hello)
            # print("calc:")
            # hello = ((exported + real_amount) * tariff)
            # supplier.decrypt_val(hello)
            t1_start = process_time()
            period_bill = (exported * trading_price - ((exported + real_amount) * tariff))
            t1_stop = process_time()
            self.timeTally += (t1_stop-t1_start)

        print("here")
        print("bill + ")
        supplier.decrypt_val(period_bill)
        # self.encryption.relinKeyGen(1, self.relinKeySize)
        # period_bill = ~ period_bill
        self.user_dict[name]['bill'] += period_bill
        print(str(supplier.encryption.noiseLevel(self.user_dict[name]['bill'])))
        supplier.decrypt_val(self.user_dict[name]['bill'])

        # trading period set to update bills once per month (48 * 30 due to there being a period every 30 minutes)
        if (period_count + 1) % (48*30) == 0:
            print("time" + str(self.timeTally))
            supplier.update_bill(name, self.user_dict[name]['bill'])
            self.user_dict[name]['bill'] = self.encryption.encryptFrac(0)

        return period_bill
