import unittest

from ledger import balance
from ledger.parse import Transaction


def tx(account, amount):
    return Transaction("2026-08-01", account, amount)


class BalanceTest(unittest.TestCase):
    def test_sums_per_account(self):
        result = balance.balances([tx("cash", 10), tx("bank", 5), tx("cash", -3)])
        self.assertEqual(result, {"cash": 7, "bank": 5})

    def test_empty(self):
        self.assertEqual(balance.balances([]), {})
        self.assertEqual(balance.total([]), 0)

    def test_total(self):
        self.assertEqual(balance.total([tx("cash", 10), tx("bank", -4)]), 6)


if __name__ == "__main__":
    unittest.main()
