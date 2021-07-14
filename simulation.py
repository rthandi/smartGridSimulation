import random
import numpy as np
from Pyfhel import Pyfhel, PyPtxt, PyCtxt
import matplotlib.pyplot as plt
from shapely.geometry import LineString

# constants
RETAIL_PRICE = 10
FEED_IN_TARIFF = 2
TRADING_PERIODS = 1

# Notes: Make it easy to compare to using the normal markets
# Look at homomorphic encrypt libs

class User:
    def __init__(self, name):
        self.name = name
        self.imported = 0
        self.exported = 0
        self.realTradeAmount = 0
        self.bill = 0
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

    cumBuy = np.array(np.cumsum(list(d['amount'] for d in buyList)))
    cumSell = np.array(np.cumsum(list(d['amount'] for d in sellList)))
    sellPriceColumn = np.array(list(d['price'] for d in sellList))
    buyPriceColumn = np.array(list(d['price'] for d in buyList))

    polyfitBuy = np.polyfit(cumBuy, buyPriceColumn, 1)
    polyfitSell = np.polyfit(cumSell, sellPriceColumn, 1)

    plt.plot(cumBuy, polyfitBuy[0]*cumBuy + polyfitBuy[1])
    plt.plot(cumSell, polyfitSell[0]*cumSell + polyfitSell[1])

    xi = ((polyfitBuy[1] - polyfitSell[1]) / (polyfitSell[0] - polyfitBuy[0]))
    yi = ((polyfitBuy[0] * xi) + polyfitBuy[1])

    print('(xi,yi)',xi,yi)
    plt.scatter(xi, yi, color='black' )

    plt.show()

    return yi

    # plt.step(cumBuy, buyPriceColumn)
    # plt.step(cumSell, sellPriceColumn)

    # plt.plot(cumBuy, buyPriceColumn)
    # plt.plot(cumSell, sellPriceColumn)
    #
    # # From: https://www.youtube.com/watch?v=heGBqav2TbU
    # line_1 = LineString(np.column_stack((cumBuy, buyPriceColumn)))
    # line_2 = LineString(np.column_stack((cumSell, sellPriceColumn)))
    # intersection = line_1.intersection(line_2)
    # if (intersection):
    #     plt.plot(*intersection.xy, 'ro')
    #     plt.show()
    #     return intersection.y
    # else:
    #     return None


def auction_winners(users_arg, importers_arg, exporters_arg):
    # calculate the trading price using bids
    trading_price = doubleAuction(importers_arg, exporters_arg)
    traders = set()
    if trading_price:
        trading_price = round(trading_price, 2)
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
        print(nonTrader)
        if nonTrader in importers_arg:
            nonTrader.bill += nonTrader.imported * RETAIL_PRICE
        else:
            nonTrader.bill -= nonTrader.exported * FEED_IN_TARIFF

    tradeVol = 0
    for export_trader in (traders - importers_arg):
        real_amount = export_trader.realTradeAmount
        committed_amount = export_trader.exported
        tradeVol += committed_amount
        if committed_amount >= real_amount:
            # they sell the committed amount or more - excess sold for FIT
            tariff = FEED_IN_TARIFF
        else:
            # they sell less than the committed amount - buy from retail
            tariff = RETAIL_PRICE
        export_trader.bill -= committed_amount * trading_price - (real_amount - committed_amount) * tariff

    for import_trader in (traders.intersection(importers_arg)):
        real_amount = import_trader.realTradeAmount
        committed_amount = import_trader.imported
        tradeVol = tradeVol - committed_amount
        if committed_amount <= real_amount:
            # they use the committed amount or more - extra purchased from retail
            tariff = RETAIL_PRICE
        else:
            # they use less than the committed amount - excess sold for FIT
            tariff = FEED_IN_TARIFF
        import_trader.bill += committed_amount * trading_price + (real_amount - committed_amount) * tariff

    print("final trade vol " + str(tradeVol))
    return traders | non_traders


def simulate(trading_periods):
    alice = User("Alice")
    bob = User("Bob")
    charlie = User("Charlie")
    dean = User("Dean")
    erin = User("Erin")
    fred = User("Fred")
    gary = User("Gary")
    harry = User("Harry")
    imogen = User("Imogen")
    john = User("John")

    users = {alice, bob, charlie, dean, erin, fred, gary, harry, imogen, john}
    importers = {alice, bob, charlie, dean, erin, fred}
    exporters = {gary, harry, imogen, john}

    for currentTradingPeriod in range(trading_periods):
        # select a bid price and export/import amount for each user
        for current_user in users:
            current_user.bid = random.randint(FEED_IN_TARIFF + 1, RETAIL_PRICE - 1)
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
        for current_user in users:
            print("name: " + current_user.name + " imported: " + str(current_user.imported) + " exported: " +
                  str(current_user.exported) + " current bill: " + str(current_user.bill))

    return users

simulate(TRADING_PERIODS)
