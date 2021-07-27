from Pyfhel import Pyfhel, PyPtxt, PyCtxt


class User:
    def __init__(self, name=None, bill=0):
        self.name = name
        self.imported = 0
        self.exported = 0
        self.realTradeAmount = 0
        self.bid = 0
        self.bill = bill

    def __str__(self):
        return "User: " + self.name + " bill: " + str(self.bill)

    def reset(self):
        self.imported = 0
        self.exported = 0
        self.realTradeAmount = 0
        self.bid = 0
