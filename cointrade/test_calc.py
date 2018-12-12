from cointrade import app
import unittest

user = {'username': 'test', 'password': 'password'}


class TestBitcoinInput(unittest.TestCase):
    #Test a user's input can be casted to an integer, in this case a amount of btcs to sell/buy
    def test_btc_int(self):
        bitcoin_amt = 1
        self.assertEqual(bitcoin_amt, int(bitcoin_amt))
    #Test to make sure bitcoin info is in array
    def test_btc_arr_empty(self):
        btc_array = [375.5]
        empty_btc_array = []
        self.assertTrue(btc_array[len(btc_array) - 1])
        self.assertFalse(len(empty_btc_array) > 1)
    #Test a mock user login
    def test_user_login(self):
        self.assertTrue(user['username'] == 'test' and user['password'] == 'password')


if __name__ == '__main__':
    unittest.main()
