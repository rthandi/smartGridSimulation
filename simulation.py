import random

# constants
RETAIL_PRICE = 10
FEED_IN_TARIFF = 2
TRADING_PERIODS = 4


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
    # const for amount to adjust prices for. Should be random but easier to test like this for now
    ADJUST_AMOUNT = 1
    imported_amount = importer.imported
    exported_amount = exporter.exported
    print("trade occurring between " + importer.name + " and " + exporter.name)
    if imported_amount > exported_amount:
        diff = imported_amount - exported_amount
        print(importer.name + " buying " + str(diff) + " for retail price " + str(RETAIL_PRICE))
        trade_amount = exported_amount
        importer.bill += diff * RETAIL_PRICE
    else:
        diff = exported_amount - imported_amount
        print(exporter.name + " selling " + str(diff) + " for feed in tariff " + str(FEED_IN_TARIFF))
        exporter.bill -= diff * FEED_IN_TARIFF
        trade_amount = imported_amount
    # trade is now committed to but there is a chance for either user to export/import more or less than they committed to
    # the case that exporter exports extra is just feed in tariff so we can assume that is covered above
    # same for the case where importer uses more - they just buy on retail
    rand_num = random.randint(1, 4)
    if rand_num == 1:
        # case where importer uses less than they committed to in the trade - they sell for fit
        print(importer.name + " used less than they bought. Selling excess for feed in")
        importer.bill -= ADJUST_AMOUNT * FEED_IN_TARIFF
    elif rand_num == 2:
        # case where exporter exports less than they committed to in the trade - they but for retail
        print(exporter.name + " exported less than they sold. Buying difference for retail")
        exporter.bill += ADJUST_AMOUNT * RETAIL_PRICE
    # Execute the trade
    trade_cost = price * trade_amount
    print(importer.name + " and " + exporter.name + " trading cost: " + str(trade_cost))
    importer.bill += trade_cost
    exporter.bill -= trade_cost
    # reset trade partners
    importer.tradePartner = None
    exporter.tradePartner = None


for currentTradingPeriod in range(TRADING_PERIODS):
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
                        trade(currentUser, tradingUser, random.randint(FEED_IN_TARIFF + 1, RETAIL_PRICE - 1))
                        importers.remove(currentUser)
                        exporters.remove(tradingUser)
                        break
            else:
                for tradingUser in importers:
                    if tradingUser.tradePartner is None:
                        tradingUser.tradePartner = currentUser
                        currentUser.tradePartner = tradingUser
                        trade(tradingUser, currentUser, random.randint(FEED_IN_TARIFF + 1, RETAIL_PRICE - 1))
                        importers.remove(tradingUser)
                        exporters.remove(currentUser)
                        break
    # For any user that did not trade with another use normal retail price or fit
    for currentUser in importers:
        currentUser.bill += currentUser.imported * RETAIL_PRICE
    for currentUser in exporters:
        currentUser.bill -= currentUser.exported * FEED_IN_TARIFF

    #for testing only
    for currentUser in users:
        print("name: " + currentUser.name + " imported: " + str(currentUser.imported) + " exported: " + str(currentUser.exported) + " current bill: " + str(currentUser.bill))