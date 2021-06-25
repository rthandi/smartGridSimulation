import random

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

users = [alice, bob, charlie, dean, erin, fred, gary]
importers = None
exporters = None

for i in range(4):
    importers = []
    exporters = []
    for j in users:
        # choose whether importer or exporter
        # More realistic to not be 50/50 but this can be changed later
        if random.randint(1,2) == 1:
            j.imported = random.randint(2, 100)
            importers.append(j)
        else:
            # Probably more realistic to expect exports are lower than imports but will leave it like this for now
            j.exported = random.randint(2, 100)
            exporters.append(j)

