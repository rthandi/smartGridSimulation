import random
import numpy as np
from Pyfhel import Pyfhel, PyPtxt, PyCtxt
import matplotlib.pyplot as plt
import intersect

# constants
RETAIL_PRICE = 10
FEED_IN_TARIFF = 2
TRADING_PERIODS = 1
USER_COUNT = 20


# Notes: Make it easy to compare to using the normal markets
# Look at homomorphic encrypt libs

class User:
    def __init__(self, name=None):
        self.name = name
        self.imported = 0
        self.exported = 0
        self.realTradeAmount = 0
        self.bill = 0
        self.bid = 0
        self.encryption = Pyfhel()
        self.encryption.contextGen(p=65537)
        self.encryption.keyGen()

    def reset(self):
        self.imported = 0
        self.exported = 0
        self.realTradeAmount = 0
        self.bid = 0


def doubleAuction(auctionImporters, auctionExporters):
    # %%% UNCOMMENT THE BLOCK BELOW FOR EASY DEBUGGING OF THIS METHOD %%%
    """"
    alice.bid = 5
    alice.exported = 20
    alice.imported = 15
    bob.bid = 15
    bob.exported = 10
    bob.imported = 27
    charlie.bid = 10
    charlie.exported = 25
    charlie.imported = 35
    dean.bid = 20
    dean.exported = 20
    dean.imported = 20
    erin.bid = 10
    erin.exported = 20
    erin.imported = 25

    auctionImporters = [alice, bob, charlie, dean, erin]
    auctionExporters = [alice, bob, charlie, dean, erin]
    """

    sellList = []
    buyList = []
    flag = None
    if len(auctionImporters) > 0 and len(auctionExporters) > 0:
        for importer in auctionImporters:
            flag = False
            for listing in sellList:
                if listing['price'] == importer.bid:
                    listing['amount'] += importer.imported
                    flag = True
            if not flag:
                sellList.append({'amount': importer.imported, 'price': importer.bid})

        for exporter in auctionExporters:
            flag = False
            for listing in buyList:
                if listing['price'] == exporter.bid:
                    listing['amount'] += exporter.exported
                    flag = True
            if not flag:
                buyList.append({'amount': exporter.exported, 'price': exporter.bid})

        sellList.sort(key=lambda item: item['price'])
        buyList.sort(key=lambda item: item['price'], reverse=True)

        cumBuy = list(np.cumsum(list(d['amount'] for d in buyList)))
        cumSell = list(np.cumsum(list(d['amount'] for d in sellList)))
        sellPriceColumn = list(d['price'] for d in sellList)
        buyPriceColumn = list(d['price'] for d in buyList)

        # this seems super inneficient but i've tried 100 other things and can't find a better way
        # using the curve values will always give a different value so it needs to be stepped like this (I think)
        for i in range(0, len(cumBuy) * 2 - 2, 2):
            cumBuy.insert(i + 1, cumBuy[i])
            buyPriceColumn.insert(i + 1, buyPriceColumn[i + 1])

        for i in range(0, len(cumSell) * 2 - 2, 2):
            cumSell.insert(i + 1, cumSell[i])
            sellPriceColumn.insert(i + 1, sellPriceColumn[i + 1])

        plt.plot(cumBuy, buyPriceColumn)
        plt.plot(cumSell, sellPriceColumn)

        x, y = intersect.intersection(cumBuy, buyPriceColumn, cumSell, sellPriceColumn)

        # prices = np.arange(FEED_IN_TARIFF, RETAIL_PRICE, 0.01)

        try:
            plt.plot(x[0], y[0], 'ro')
            plt.show()
            return y[0]
        except IndexError:
            return None
    else:
        print("Importers or exporters is empty")
        return None

def auction_winners(users_arg, importers_arg, exporters_arg):
    # calculate the trading price using bids
    trading_price = doubleAuction(importers_arg, exporters_arg)
    traders = set()
    if trading_price:
        trading_price = trading_price
        print("Trading price for this trading period is: " + str(trading_price))
        for current_user in users_arg:
            # for each user we see if their bid is in the correct range to trade
            if (current_user in importers_arg and current_user.bid >= trading_price
                    or current_user in exporters_arg and current_user.bid <= trading_price):
                traders.add(current_user)
    else:
        print("No intersection of supply demand curves - no trading will occur this period")

    non_traders = users_arg - traders

    return traders, non_traders, trading_price


def set_up_trades(traders, non_traders, importers_arg, trading_price):
    for non_trader in non_traders:
        if non_trader in importers_arg:
            # user's import amount is encrypted before being sent to the trading platform for execution
            non_trader.imported = non_trader.encryption.encryptFrac(non_trader.imported)
            non_trader.realTradeAmount = non_trader.imported
            execute_trade(non_trader, 0, RETAIL_PRICE)
            # This commented method is an alternative - it should be more efficient but makes it hard/messier to
            # simulate it being run on the trading platform
            # non_trader.bill = (non_trader.imported * RETAIL_PRICE) + non_trader.bill
        else:
            non_trader.exported = non_trader.encryption.encryptFrac(non_trader.exported)
            non_trader.realTradeAmount = non_trader.exported
            execute_trade(non_trader, 0, FEED_IN_TARIFF)
            # non_trader.bill = (non_trader.exported * FEED_IN_TARIFF) + non_trader.bill
        non_trader.reset()

    # TODO: These two blocks can be simplified to one method
    volumeTraded = 0
    for export_trader in (traders - importers_arg):
        volumeTraded += export_trader.exported
        if export_trader.exported >= export_trader.realTradeAmount:
            # they sell the committed amount or more - excess sold for FIT
            tariff = FEED_IN_TARIFF
        else:
            # they sell less than the committed amount - buy from retail
            tariff = RETAIL_PRICE
        # encrypt user's data before it is sent to trading platform to execute the trade
        export_trader.exported = export_trader.encryption.encryptFrac(export_trader.exported)
        export_trader.realTradeAmount = export_trader.encryption.encryptFrac(export_trader.realTradeAmount)
        execute_trade(export_trader, tariff, trading_price)
        export_trader.reset()

    for import_trader in (traders.intersection(importers_arg)):
        volumeTraded -= import_trader.imported
        if import_trader.imported <= import_trader.realTradeAmount:
            # they use the committed amount or more - extra purchased from retail
            tariff = RETAIL_PRICE
        else:
            # they use less than the committed amount - excess sold for FIT
            tariff = FEED_IN_TARIFF
        # encrypt user's data before it is sent to trading platform to execute the trade
        import_trader.imported = import_trader.encryption.encryptFrac(import_trader.imported)
        import_trader.realTradeAmount = import_trader.encryption.encryptFrac(import_trader.realTradeAmount)
        execute_trade(import_trader, tariff, trading_price)
        import_trader.reset()

    print("difference between amount exported and imported (this should be 0):  " + str(volumeTraded))
    return traders | non_traders

def execute_trade(user, tariff, trading_price):
    # this simulates the calculations run on the trading platform
    real_amount = user.realTradeAmount
    imported = user.imported
    # bill calculations are in a very weird order so that they work for Pyfhel's methods as they take the + and *
    # operators and call their own methods from those in which the first argument must be a Pyfhel object
    if user.imported:
        user.bill = (imported * trading_price - ((real_amount - imported) * tariff)) + user.bill
    else:
        exported = user.exported
        user.bill = exported * trading_price - ((real_amount - exported) * tariff) + user.bill

def simulate(trading_periods):
    # alice = User("Alice")
    # bob = User("Bob")
    # charlie = User("Charlie")
    # dean = User("Dean")
    # erin = User("Erin")
    # fred = User("Fred")
    # gary = User("Gary")
    # harry = User("Harry")
    # imogen = User("Imogen")
    # john = User("John")
    #
    # users = {alice, bob, charlie, dean, erin, fred, gary, harry, imogen, john}
    # importers = {alice, bob, charlie, dean, erin, fred}
    # exporters = {gary, harry, imogen, john}

    users = set()
    importers = set()
    exporters = set()
    for i in range(USER_COUNT):
        users.add(User(str(i)))

    for user in users:
        if random.randint(1, 2) == 1:
            exporters.add(user)
        else:
            importers.add(user)

    for currentTradingPeriod in range(trading_periods):
        # select a bid price and export/import amount for each user
        for current_user in users:
            current_user.bid = round(random.uniform(FEED_IN_TARIFF + 1, RETAIL_PRICE - 1), 2)
            if current_user in importers:
                current_user.imported = random.randint(5, 50)
            else:
                current_user.exported = random.randint(5, 50)

        traders, non_traders, trading_price = auction_winners(users, importers, exporters)

        for trader in traders:
            # random chance for real amount traded to be different to amount committed to in bid
            if random.randint(1, 4) == 1:
                trader.realTradeAmount = random.randint(5, 50)
            else:
                trader.realTradeAmount = max(trader.exported, trader.imported)

        users = set_up_trades(traders, non_traders, importers, trading_price)

        # for testing only
        for current_user in users:
            # print("name: " + current_user.name + " imported: " + str(current_user.imported) + " exported: " +
            #       str(current_user.exported) + " current bill: " + str(current_user.bill))
            print("name: " + current_user.name + " bill: " +
                  str(round(current_user.encryption.decryptFrac(current_user.bill), 2)))

    return users


simulate(TRADING_PERIODS)
