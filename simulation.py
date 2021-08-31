import random
import numpy as np
import intersect

from TradingPlatform import TradingPlatform
from User import User
from Supplier import Supplier

# constants
RETAIL_PRICE = 10
FEED_IN_TARIFF = 2
MONTHS = 48*30
USER_COUNT = 10

#                                                        %%% CONFIG %%%
# false means no trading will occur
TRADE_MODE = True
TRADING_PERIODS = 1 * MONTHS


def double_auction(auction_importers, auction_exporters):
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
        # a smooth one which seems to never give the correct values
        for i in range(0, len(cum_buy) * 2 - 2, 2):
            cum_buy.insert(i + 1, cum_buy[i + 1])
            buy_price_column.insert(i + 1, buy_price_column[i])

        for i in range(0, len(cum_sell) * 2 - 2, 2):
            cum_sell.insert(i + 1, cum_sell[i + 1])
            sell_price_column.insert(i + 1, sell_price_column[i])

        x, y = intersect.intersection(cum_buy, buy_price_column, cum_sell, sell_price_column)

        try:
            # uncomment to see graphs - good for debugging auction system
            # plt.plot(cum_buy, buy_price_column)
            # plt.plot(cum_sell, sell_price_column)
            # plt.plot(x[0], y[0], 'ro')
            # plt.show()
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
    if trading_price and TRADE_MODE:
        trading_price = trading_price
        for current_user in users_arg:
            # for each user we see if their bid is in the correct range to trade
            if (current_user in importers_arg and current_user.bid >= trading_price
                    or current_user in exporters_arg and current_user.bid <= trading_price):
                traders.add(current_user)
    elif not TRADE_MODE:
        print("Trade mode is not active")
    else:
        print("No intersection of supply demand curves - no trading will occur this period")

    non_traders = users_arg - traders

    return traders, non_traders, trading_price


def set_up_trades(traders, non_traders, importers_arg, trading_price, trading_platform, supplier_encrypt, supplier,
                  period_count):
    for non_trader in non_traders:
        if non_trader in importers_arg:
            # user's import amount is encrypted before being sent to the trading platform for execution
            import_encrypt = non_trader.get_encrypted_import()
            # execute trade on the trading platform
            trading_platform.execute_trade(non_trader.name, import_encrypt,
                                           import_encrypt, RETAIL_PRICE, 0, True, supplier, period_count)
            # execute the same trade on the user's smart meter
            non_trader.execute_trade(non_trader.imported, non_trader.imported, RETAIL_PRICE, 0, True)
        else:
            export_encrypt = non_trader.get_encrypted_exported()
            # execute trade on the trading platform
            trading_platform.execute_trade(non_trader.name, export_encrypt, export_encrypt,
                                           FEED_IN_TARIFF, 0, False, supplier, period_count)
            # execute the same trade on the user's smart meter
            non_trader.execute_trade(non_trader.exported, non_trader.exported, FEED_IN_TARIFF, 0, False)
        non_trader.reset()

    for import_trader in (traders.intersection(importers_arg)):
        if import_trader.imported <= import_trader.realTradeAmount:
            # they use the committed amount or more - extra purchased from retail
            tariff = RETAIL_PRICE
        else:
            # they use less than the committed amount - excess sold for FIT
            tariff = FEED_IN_TARIFF
        # encrypt user's data before it is sent to trading platform to execute the trade
        import_encrypt = import_trader.get_encrypted_import()
        real_encrypt = import_trader.get_encrypted_real_amount()
        # execute trade on the trading platform
        trading_platform.execute_trade(import_trader.name, import_encrypt, real_encrypt,
                                       trading_price, tariff, True, supplier, period_count)
        # execute the same trade on the user's smart meter - in plaintext as it won't be sent anywhere
        import_trader.execute_trade(import_trader.imported, import_trader.realTradeAmount, trading_price, tariff, True)
        import_trader.reset()

    for export_trader in (traders - importers_arg):
        if export_trader.exported >= export_trader.realTradeAmount:
            # they sell the committed amount or more - excess sold for FIT
            tariff = FEED_IN_TARIFF
        else:
            # they sell less than the committed amount - buy from retail
            tariff = RETAIL_PRICE
        # encrypt user's data before it is sent to trading platform to execute the trade
        export_encrypt = export_trader.get_encrypted_exported()
        real_encrypt = export_trader.get_encrypted_real_amount()
        # execute trade on the trading platform
        trading_platform.execute_trade(export_trader.name, export_encrypt, real_encrypt,
                                       trading_price, tariff, False, supplier, period_count)
        # execute the same trade on the user's smart meter
        export_trader.execute_trade(export_trader.exported, export_trader.realTradeAmount, trading_price, tariff, False)
        export_trader.reset()

    return traders | non_traders


def simulate(trading_periods):
    supplier = Supplier()
    supplier_encrypt = supplier.get_paillier_public_key()
    supplier_rsa_key = supplier.get_rsa_public_key()

    trading_platform = TradingPlatform()

    users = set()
    importers = set()
    exporters = set()
    for i in range(USER_COUNT):
        users.add(User(supplier_rsa_key, supplier_encrypt, str(i)))
        print("Added user:" + str(i))

    supplier.load_users(users)
    trading_platform.load_users(users)

    print("running...")

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

        users = set_up_trades(traders, non_traders, importers, trading_price, trading_platform, supplier_encrypt,
                              supplier, currentTradingPeriod)

    for current_user in users:
        current_user.verify_send(supplier)

    return users


simulate(TRADING_PERIODS)
