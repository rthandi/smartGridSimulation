import unittest
import simulation

class testMain(unittest.TestCase):
    def testEasy(self):
        random_numbers = [1, 2, 2, 1, 2, 2, 1, 2, 2, 1, 2, 2, 1, 2, 2, 1, 2, 2, 1, 2, 2, 1, 2, 2]
        simulation.random.randint = lambda self, n: random_numbers.pop(0)

        run = simulation.simulate(1)
        self.assertEqual(20, run[0].bill)
