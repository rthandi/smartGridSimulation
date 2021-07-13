import unittest
import simulation

class doubleAuctionTest(unittest.TestCase):
    def setUp(self):
        alice = simulation.User("Alice")
        bob = simulation.User("Bob")
        charlie = simulation.User("Charlie")
        dean = simulation.User("Dean")

    def testMatchingPrices:

