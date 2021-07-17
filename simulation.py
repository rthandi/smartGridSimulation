import random
import numpy as np
from Pyfhel import Pyfhel, PyPtxt, PyCtxt
import matplotlib.pyplot as plt
import intersect

# constants
RETAIL_PRICE = 10
FEED_IN_TARIFF = 2
TRADING_PERIODS = 1
USER_COUNT = 1000


# Notes: Make it easy to compare to using the normal markets
# Look at homomorphic encrypt libs

class User:
    def __init__(self, name = None):
        self.name = name
        self.imported = 0
        self.exported = 0
        self.realTradeAmount = 0
        self.bill = 0
        self.bid = 0

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


def execute_trades(traders, non_traders, importers_arg, trading_price):
    for nonTrader in non_traders:
        if nonTrader in importers_arg:
            nonTrader.bill += nonTrader.imported * RETAIL_PRICE
        else:
            nonTrader.bill -= nonTrader.exported * FEED_IN_TARIFF
        nonTrader.reset()

    volumeTraded = 0
    for export_trader in (traders - importers_arg):
        real_amount = export_trader.realTradeAmount
        committed_amount = export_trader.exported
        volumeTraded += committed_amount
        if committed_amount >= real_amount:
            # they sell the committed amount or more - excess sold for FIT
            tariff = FEED_IN_TARIFF
        else:
            # they sell less than the committed amount - buy from retail
            tariff = RETAIL_PRICE
        export_trader.bill -= committed_amount * trading_price - ((real_amount - committed_amount) * tariff)
        export_trader.reset()

    for import_trader in (traders.intersection(importers_arg)):
        real_amount = import_trader.realTradeAmount
        committed_amount = import_trader.imported
        volumeTraded -= committed_amount
        if committed_amount <= real_amount:
            # they use the committed amount or more - extra purchased from retail
            tariff = RETAIL_PRICE
        else:
            # they use less than the committed amount - excess sold for FIT
            tariff = FEED_IN_TARIFF
        import_trader.bill += committed_amount * trading_price + ((real_amount - committed_amount) * tariff)
        import_trader.reset()

    print("difference between amount exported and imported (this should be 0):  " + str(volumeTraded))
    return traders | non_traders


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

        users = execute_trades(traders, non_traders, importers, trading_price)

        # for testing only
        # for current_user in users:
        #     print("name: " + current_user.name + " imported: " + str(current_user.imported) + " exported: " +
        #           str(current_user.exported) + " current bill: " + str(current_user.bill))

    return users


simulate(TRADING_PERIODS)
