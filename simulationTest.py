import copy
import unittest
import simulation

class doubleAuctionTest(unittest.TestCase):

    alice = simulation.User("Alice")
    bob = simulation.User("Bob")
    charlie = simulation.User("Charlie")
    dean = simulation.User("Dean")
    erin = simulation.User("Erin")
    fred = simulation.User("Fred")

    alice.bid = 5
    alice.exported = 20
    alice.imported = 10
    bob.bid = 10
    bob.exported = 20
    bob.imported = 20
    charlie.bid = 10
    charlie.exported = 20
    charlie.imported = 20
    dean.bid = 5
    dean.exported = 20
    dean.imported = 20
    erin.bid = 5
    erin.exported = 20
    erin.imported = 35
    fred.bid = 2
    fred.exported = 10
    fred.imported = 50

    auction_importers = set()
    auction_exporters = set()
    users = set()

    def testOneImporter(self):
        self.auction_importers = {self.alice}
        res = simulation.doubleAuction(self.auction_importers, self.auction_exporters)
        self.assertEqual(res, None)

    def testOneExporter(self):
        self.auction_exporters = {self.alice}
        res = simulation.doubleAuction(self.auction_importers, self.auction_exporters)
        self.assertEqual(res, None)

    def testNoIntersection(self):
        self.auction_importers = {self.alice}
        self.auction_exporters = {self.bob}
        res = simulation.doubleAuction(self.auction_importers, self.auction_exporters)
        self.assertEqual(res, None)

    def testIntersectionEven(self):
        self.auction_importers = {self.charlie, self.dean}
        self.auction_exporters = {self.alice, self.bob}
        res = simulation.doubleAuction(self.auction_importers, self.auction_exporters)
        self.assertEqual(res, 10)

    def testIntersectionUnevenImport(self):
        self.auction_importers = {self.charlie, self.erin}
        self.auction_exporters = {self.alice, self.bob}
        res = simulation.doubleAuction(self.auction_importers, self.auction_exporters)
        self.assertEqual(res, 5)

    def testCurve(self):
        self.auction_importers = {self.charlie, self.erin, self.fred}
        self.auction_exporters = {self.alice, self.bob, self.dean}
        res = simulation.doubleAuction(self.auction_importers, self.auction_exporters)
        self.assertEqual(res, 5)



    # def testTradeRun(self):
    #     self.auction_importers = {self.charlie, self.dean}
    #     self.auction_exporters = {self.alice, self.bob}
    #     self.users = {self.charlie, self.dean, self.alice, self.bob}
    #     users_copy = copy.deepcopy(self.users)
    #     res_price = simulation.doubleAuction(self.auction_importers, self.auction_exporters)
    #     self.assertEqual(res_price, 7.5)
    #     traders, non_traders, trading_price = simulation.auction_winners(self.users, self.auction_importers,
    #                                                                      self.auction_exporters)
    #     res_users = simulation.execute_trades(traders, non_traders, self.auction_importers, trading_price)
    #     price_dean = res_users.pop().bill
    #     self.assertEqual(price_dean, users_copy.pop().imported * simulation.RETAIL_PRICE)
    #     price_charlie = res_users.pop().bill
    #     self.assertEqual(price_charlie, users_copy.pop().imported * res_price)
    #     print(res_users.pop().name)

    class auctionWinnersTest(unittest.TestCase):

        alice = simulation.User("Alice")
        bob = simulation.User("Bob")
        charlie = simulation.User("Charlie")
        dean = simulation.User("Dean")
        erin = simulation.User("Erin")
        fred = simulation.User("Fred")

        alice.bid = 5
        alice.exported = 20
        alice.imported = 10
        bob.bid = 10
        bob.exported = 20
        bob.imported = 20
        charlie.bid = 10
        charlie.exported = 20
        charlie.imported = 20
        dean.bid = 5
        dean.exported = 20
        dean.imported = 20
        erin.bid = 5
        erin.exported = 20
        erin.imported = 35
        fred.bid = 2
        fred.exported = 10
        fred.imported = 50

        auction_importers = set()
        auction_exporters = set()
        users = set()
