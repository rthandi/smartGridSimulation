from Pyfhel import Pyfhel, PyPtxt, PyCtxt

class User:
    def __init__(self, name=None):
        self.name = name
        self.imported = 0
        self.exported = 0
        self.realTradeAmount = 0
        self.bid = 0
        self.encryption = Pyfhel()
        self.encryption.contextGen(p=65537)
        self.encryption.keyGen()
        self.bill = self.encryption.encryptFrac(0)

    def __str__(self):
        return "User: " + self.name + " bill: " + str(round(self.encryption.decryptFrac(self.bill), 2))

    def reset(self):
        self.imported = 0
        self.exported = 0
        self.realTradeAmount = 0
        self.bid = 0
