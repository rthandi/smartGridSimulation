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


def trade(importer, exporter, price):
    # Random chance for


for currentTradingPeriod in range(4):
    importers = []
    exporters = []
    for currentUser in users:
        # choose whether importer or exporter
        # More realistic to not be 50/50 but this can be changed later
        if random.randint(1, 2) == 1:
            currentUser.imported = random.randint(2, 100)
            importers.append(currentUser)
        else:
            # Probably more realistic to expect exports are lower than imports but will leave it like this for now
            currentUser.exported = random.randint(2, 100)
            exporters.append(currentUser)
        # Select if trader  (1 in 3 chance for now)
        if random.randint(1, 3) == 1:
            #If an imported find an exporter and vice versa
            if currentUser in importers:
                for tradingUser in exporters:
                    if tradingUser.tradePartner is None:
                        tradingUser.tradePartner = currentUser
                        currentUser.tradePartner = tradingUser
                        trade(currentUser, tradingUser, random.randint(feedInTariff + 1, retailPrice - 1))
            else:
                for tradingUser in importers:
                    if tradingUser.tradePartner is None:
                        tradingUser.tradePartner = currentUser
                        currentUser.tradePartner = tradingUser
                        trade(tradingUser, currentUser, random.randint(feedInTariff + 1, retailPrice - 1))
                

