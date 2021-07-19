from unittest import TestCase

import Pyfhel.PyCtxt
from Pyfhel import PyCtxt, PyPtxt
from TradingPlatform import TradingPlatform
from User import User

class TestTradingPlatform(TestCase):
    trading_platform = TradingPlatform()

    def setUp(self) -> None:
        self.trading_platform = TradingPlatform()

    def test_load_users_empty(self):
        self.trading_platform.load_users(set())
        self.assertEqual(self.trading_platform.userDict, {})

    def test_load_users_one(self):
        alice = User('Alice')
        self.trading_platform.load_users({alice})
        self.assertEqual(self.trading_platform.userDict['Alice'].name, 'Alice')
        self.assertIsInstance(self.trading_platform.userDict['Alice'].context, bytes)
        self.assertIsInstance(self.trading_platform.userDict['Alice'].public_key, bytes)
        self.assertEqual(len(self.trading_platform.userDict), 1)

    def test_load_users_multiple(self):
        alice = User('Alice')
        bob = User('Bob')
        charlie = User('Charlie')
        self.trading_platform.load_users({alice, bob, charlie})
        self.assertEqual(self.trading_platform.userDict['Alice'].name, 'Alice')
        self.assertIsInstance(self.trading_platform.userDict['Alice'].context, bytes)
        self.assertIsInstance(self.trading_platform.userDict['Alice'].public_key, bytes)
        self.assertEqual(self.trading_platform.userDict['Bob'].name, 'Bob')
        self.assertIsInstance(self.trading_platform.userDict['Bob'].context, bytes)
        self.assertIsInstance(self.trading_platform.userDict['Bob'].public_key, bytes)
        self.assertEqual(self.trading_platform.userDict['Charlie'].name, 'Charlie')
        self.assertIsInstance(self.trading_platform.userDict['Charlie'].context, bytes)
        self.assertIsInstance(self.trading_platform.userDict['Charlie'].public_key, bytes)
        self.assertEqual(len(self.trading_platform.userDict), 3)

    def test_execute_trade_no_change_import(self):
        alice = User('Alice')
        bob = User('Bob')
        charlie = User('Charlie')
        self.trading_platform.load_users({alice, bob, charlie})
        committed_amount = alice.encryption.encryptFrac(10)
        real_amount = alice.encryption.encryptFrac(0)

        # check is encrypted
        res_execute = self.trading_platform.execute_trade(alice.name, committed_amount, real_amount, 5, 0, True)
        self.assertIsInstance(res_execute, PyCtxt)

        # check trading platform cannot decrypt
        res_decrypt_fail = self.trading_platform.encryption.decryptFrac(res_execute)
        self.assertNotEqual(res_decrypt_fail, 50)

        # check user can decrypt
        res_decrypt_succeed = alice.encryption.decryptFrac(res_execute)
        self.assertEqual(res_decrypt_succeed, 50)

    def test_execute_trade_no_change_export(self):
        alice = User('Alice')
        bob = User('Bob')
        charlie = User('Charlie')
        self.trading_platform.load_users({alice, bob, charlie})
        committed_amount = alice.encryption.encryptFrac(10)
        real_amount = alice.encryption.encryptFrac(0)

        # check is encrypted
        res_execute = self.trading_platform.execute_trade(alice.name, committed_amount, real_amount, 5, 0, False)
        self.assertIsInstance(res_execute, PyCtxt)

        # check trading platform cannot decrypt
        res_decrypt_fail = self.trading_platform.encryption.decryptFrac(res_execute)
        self.assertNotEqual(res_decrypt_fail, -50)

        # check user can decrypt
        res_decrypt_succeed = alice.encryption.decryptFrac(res_execute)
        self.assertEqual(res_decrypt_succeed, -50)

    def test_execute_trade_change_less_import(self):
        alice = User('Alice')
        bob = User('Bob')
        charlie = User('Charlie')
        self.trading_platform.load_users({alice, bob, charlie})
        committed_amount = alice.encryption.encryptFrac(10)
        real_amount = alice.encryption.encryptFrac(8)

        # check is encrypted
        res_execute = self.trading_platform.execute_trade(alice.name, committed_amount, real_amount, 5, 2, True)
        self.assertIsInstance(res_execute, PyCtxt)

        # check trading platform cannot decrypt
        res_decrypt_fail = self.trading_platform.encryption.decryptFrac(res_execute)
        self.assertNotEqual(res_decrypt_fail, 46)

        # check user can decrypt
        res_decrypt_succeed = alice.encryption.decryptFrac(res_execute)
        self.assertEqual(res_decrypt_succeed, 46)

    def test_execute_trade_change_more_import(self):
        alice = User('Alice')
        bob = User('Bob')
        charlie = User('Charlie')
        self.trading_platform.load_users({alice, bob, charlie})
        committed_amount = alice.encryption.encryptFrac(10)
        real_amount = alice.encryption.encryptFrac(12)

        # check is encrypted
        res_execute = self.trading_platform.execute_trade(alice.name, committed_amount, real_amount, 5, 10, True)
        self.assertIsInstance(res_execute, PyCtxt)

        # check trading platform cannot decrypt
        res_decrypt_fail = self.trading_platform.encryption.decryptFrac(res_execute)
        self.assertNotEqual(res_decrypt_fail, 70)

        # check user can decrypt
        res_decrypt_succeed = alice.encryption.decryptFrac(res_execute)
        self.assertEqual(res_decrypt_succeed, 70)

    def test_execute_trade_change_less_export(self):
        alice = User('Alice')
        bob = User('Bob')
        charlie = User('Charlie')
        self.trading_platform.load_users({alice, bob, charlie})
        committed_amount = alice.encryption.encryptFrac(10)
        real_amount = alice.encryption.encryptFrac(8)

        # check is encrypted
        res_execute = self.trading_platform.execute_trade(alice.name, committed_amount, real_amount, 5, 10, False)
        self.assertIsInstance(res_execute, PyCtxt)

        # check trading platform cannot decrypt
        res_decrypt_fail = self.trading_platform.encryption.decryptFrac(res_execute)
        self.assertNotEqual(res_decrypt_fail, -30)

        # check user can decrypt
        res_decrypt_succeed = alice.encryption.decryptFrac(res_execute)
        self.assertEqual(res_decrypt_succeed, -30)

    def test_execute_trade_change_more_export(self):
        alice = User('Alice')
        bob = User('Bob')
        charlie = User('Charlie')
        self.trading_platform.load_users({alice, bob, charlie})
        committed_amount = alice.encryption.encryptFrac(10)
        real_amount = alice.encryption.encryptFrac(12)

        # check is encrypted
        res_execute = self.trading_platform.execute_trade(alice.name, committed_amount, real_amount, 5, 2, False)
        self.assertIsInstance(res_execute, PyCtxt)

        # check trading platform cannot decrypt
        res_decrypt_fail = self.trading_platform.encryption.decryptFrac(res_execute)
        self.assertNotEqual(res_decrypt_fail, -54)

        # check user can decrypt
        res_decrypt_succeed = alice.encryption.decryptFrac(res_execute)
        self.assertEqual(res_decrypt_succeed, -54)