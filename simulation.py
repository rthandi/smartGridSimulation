import random
import numpy as np
from Pyfhel import Pyfhel, PyPtxt, PyCtxt
import matplotlib.pyplot as plt
import intersect

from TradingPlatform import TradingPlatform
from User import User

# constants
RETAIL_PRICE = 10
FEED_IN_TARIFF = 2
TRADING_PERIODS = 1
USER_COUNT = 20


def double_auction(auction_importers, auction_exporters):
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

    sell_list = []
    buy_list = []
    flag = None
    if len(auction_importers) > 0 and len(auction_exporters) > 0:
        for importer in auction_importers:
            flag = False
            for listing in sell_list:
                if listing['price'] == importer.bid:
                    listing['amount'] += importer.imported
                    flag = True
            if not flag:
                sell_list.append({'amount': importer.imported, 'price': importer.bid})

        for exporter in auction_exporters:
            flag = False
            for listing in buy_list:
                if listing['price'] == exporter.bid:
                    listing['amount'] += exporter.exported
                    flag = True
            if not flag:
                buy_list.append({'amount': exporter.exported, 'price': exporter.bid})

        sell_list.sort(key=lambda item: item['price'])
        buy_list.sort(key=lambda item: item['price'], reverse=True)

        cum_buy = list(np.cumsum(list(d['amount'] for d in buy_list)))
        cum_sell = list(np.cumsum(list(d['amount'] for d in sell_list)))
        sell_price_column = list(d['price'] for d in sell_list)
        buy_price_column = list(d['price'] for d in buy_list)

        # Not certain this is the way to do this - it creates all of the points in a stepped graph rather than
        # a smooth one which seems to
        for i in range(0, len(cum_buy) * 2 - 2, 2):
            cum_buy.insert(i + 1, cum_buy[i + 1])
            buy_price_column.insert(i + 1, buy_price_column[i])

        for i in range(0, len(cum_sell) * 2 - 2, 2):
            cum_sell.insert(i + 1, cum_sell[i + 1])
            sell_price_column.insert(i + 1, sell_price_column[i])

        plt.plot(cum_buy, buy_price_column)
        plt.plot(cum_sell, sell_price_column)

        x, y = intersect.intersection(cum_buy, buy_price_column, cum_sell, sell_price_column)

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
    trading_price = double_auction(importers_arg, exporters_arg)
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


def set_up_trades(traders, non_traders, importers_arg, trading_price, trading_platform):
    for non_trader in non_traders:
        if non_trader in importers_arg:
            # user's import amount is encrypted before being sent to the trading platform for execution
            non_trader.imported = non_trader.encryption.encryptFrac(non_trader.imported)
            non_trader.realTradeAmount = non_trader.imported
            trade_cost = trading_platform.execute_trade(non_trader.name, non_trader.imported, 0, RETAIL_PRICE, 0, True)
            non_trader.bill += trade_cost
            # This commented method is an alternative - it should be more efficient but makes it hard/messier to
            # simulate it being run on the trading platform
            # non_trader.bill = (non_trader.imported * RETAIL_PRICE) + non_trader.bill
        else:
            non_trader.exported = non_trader.encryption.encryptFrac(non_trader.exported)
            non_trader.realTradeAmount = non_trader.exported
            trade_cost = trading_platform.execute_trade(non_trader.name, non_trader.exported, 0, FEED_IN_TARIFF, 0,
                                                        False)
            non_trader.bill += trade_cost
        non_trader.reset()

    # TODO: These two blocks can be simplified to one method
    volume_traded = 0
    for import_trader in (traders.intersection(importers_arg)):
        volume_traded -= import_trader.imported
        if import_trader.imported <= import_trader.realTradeAmount:
            # they use the committed amount or more - extra purchased from retail
            tariff = RETAIL_PRICE
        else:
            # they use less than the committed amount - excess sold for FIT
            tariff = FEED_IN_TARIFF
        # encrypt user's data before it is sent to trading platform to execute the trade
        import_trader.imported = import_trader.encryption.encryptFrac(import_trader.imported)
        import_trader.realTradeAmount = import_trader.encryption.encryptFrac(import_trader.realTradeAmount)
        trade_cost = trading_platform.execute_trade(import_trader.name, import_trader.imported,
                                                    import_trader.realTradeAmount, trading_price, tariff, True)
        import_trader.bill += trade_cost
        import_trader.reset()

    for export_trader in (traders - importers_arg):
        volume_traded += export_trader.exported
        if export_trader.exported >= export_trader.realTradeAmount:
            # they sell the committed amount or more - excess sold for FIT
            tariff = FEED_IN_TARIFF
        else:
            # they sell less than the committed amount - buy from retail
            tariff = RETAIL_PRICE
        # encrypt user's data before it is sent to trading platform to execute the trade
        export_trader.exported = export_trader.encryption.encryptFrac(export_trader.exported)
        export_trader.realTradeAmount = export_trader.encryption.encryptFrac(export_trader.realTradeAmount)
        trade_cost = trading_platform.execute_trade(export_trader.name, export_trader.exported,
                                                    export_trader.realTradeAmount, trading_price, tariff, False)
        export_trader.bill -= trade_cost
        export_trader.reset()

    # TODO: This does not work :((((
    print("difference between amount exported and imported (this should be 0):  " + str(volume_traded))
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

    trading_platform = TradingPlatform()
    trading_platform.load_users(users)

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

        users = set_up_trades(traders, non_traders, importers, trading_price, trading_platform)

        # for testing only
        for current_user in users:
            print(str(current_user))

    return users


simulate(TRADING_PERIODS)
