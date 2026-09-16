import unittest

from ledger import balance
from ledger.parse import Transaction


def tx(account, amount, date="2026-08-01"):
    return Transaction(date, account, amount)


class BalanceTest(unittest.TestCase):
    def test_sums_per_account(self):
        result = balance.balances([tx("cash", 10), tx("bank", 5), tx("cash", -3)])
        self.assertEqual(result, {"cash": 7, "bank": 5})

    def test_empty(self):
        self.assertEqual(balance.balances([]), {})
        self.assertEqual(balance.total([]), 0)

    def test_total(self):
        self.assertEqual(balance.total([tx("cash", 10), tx("bank", -4)]), 6)

    def test_balances_for_month(self):
        transactions = [
            tx("cash", 10, date="2026-08-01"),
            tx("cash", 5, date="2026-08-15"),
            tx("bank", 3, date="2026-08-20"),
            tx("cash", 100, date="2026-09-01"),
        ]
        result = balance.balances_for_month(transactions, "2026-08")
        self.assertEqual(result, {"cash": 15, "bank": 3})

    def test_balances_for_month_no_matches(self):
        self.assertEqual(balance.balances_for_month([tx("cash", 10)], "2026-01"), {})


if __name__ == "__main__":
    unittest.main()
