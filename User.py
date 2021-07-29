from Pyfhel import Pyfhel, PyPtxt, PyCtxt


class User:
    def __init__(self, key, name=None, bill=0):
        self.name = name
        self.imported = 0
        self.exported = 0
        self.realTradeAmount = 0
        self.bid = 0
        self.bill = bill
        self.encryption = Pyfhel()
        self.encryption.contextGen(p=65537)
        self.encryption.from_bytes_publicKey(key)

    def __str__(self):
        return "User: " + self.name + " bill: " + str(self.bill)

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
