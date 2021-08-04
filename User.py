from HEMS import HEMS


class User:
    def __init__(self, supplier_rsa_key, name=None):
        self.name = name
        self.imported = 0
        self.exported = 0
        self.realTradeAmount = 0
        self.bid = 0
        self.HEMS = HEMS(self.name, supplier_rsa_key)

    def __str__(self):
        return "User: " + self.name + " bill: " + str(self.HEMS.bill)

    def get_public_key(self):
        return self.HEMS.get_public_key()

    def reset(self):
        self.imported = 0
        self.exported = 0
        self.realTradeAmount = 0
        self.bid = 0

    def execute_trade(self, committed_amount, real_amount, trading_price, tariff, imported):
        self.HEMS.execute_trade(committed_amount, real_amount, trading_price, tariff, imported)

    def verify_send(self, supplier):
        self.HEMS.verify_send(supplier)
