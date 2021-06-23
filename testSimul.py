retailPrice = 10
feedInTariff = 2

class User:
    def __init__(self, name):
        self.name = name
        self.imported = 0
        self.exported = 0
        self.bill = 0
        self.tradePartner = None

alice = User("Alice")
bob = User("Bob")
charlie = User("Charlie")
dean = User("Dean")
erin = User("Erin")
fred = User("Fred")
gary = User("Gary")

for i in range(4):
