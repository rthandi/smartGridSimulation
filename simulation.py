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
    importedAmount = importer.imported
    exportedAmount = exporter.exported
    print("trade occurring between " + importer.name + " and " + exporter.name)
    if importedAmount >= exportedAmount:
        # If importing larger than exporting (or the same) then the difference is made from retail market (0 when same)
        print("Importing " + str(exportedAmount) + " for " + str(price))
        exported_price = exportedAmount * price
        importer.bill += exported_price + (importedAmount - exportedAmount) * retailPrice
        exporter.bill -= exported_price
    else:
        # If exporting is larger than importing then difference is sold at fit
        print("Exporting " + str(importedAmount) + " for " + str(price))
        importedPrice = importedAmount * price
        importer.bill += importedPrice
        exporter.bill -= importedPrice + (exportedAmount - importedAmount) * feedInTariff
    # reset trade partners
    importer.tradePartner = None
    exporter.tradePartner = None


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
                        importers.remove(currentUser)
                        exporters.remove(tradingUser)
                        break
            else:
                for tradingUser in importers:
                    if tradingUser.tradePartner is None:
                        tradingUser.tradePartner = currentUser
                        currentUser.tradePartner = tradingUser
                        trade(tradingUser, currentUser, random.randint(feedInTariff + 1, retailPrice - 1))
                        importers.remove(tradingUser)
                        exporters.remove(currentUser)
                        break
    # For any user that did not trade with another use normal retail price or fit
    for currentUser in importers:
        currentUser.bill += currentUser.imported * retailPrice
    for currentUser in exporters:
        currentUser.bill -= currentUser.exported * feedInTariff

    #for testing only
    for currentUser in users:
        print("name: " + currentUser.name + " imported: " + str(currentUser.imported) + " exported: " + str(currentUser.exported) + " current bill: " + str(currentUser.bill))