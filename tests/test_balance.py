import unittest
from decimal import Decimal

from ledger import balance
from ledger.parse import Transaction


def tx(account, amount, date="2026-08-01"):
    return Transaction(date, account, amount)


class BalanceTest(unittest.TestCase):
    def test_sums_per_account(self):
        result = balance.balances([tx("cash", Decimal("10")), tx("bank", Decimal("5")), tx("cash", Decimal("-3"))])
        self.assertEqual(result, {"cash": Decimal("7"), "bank": Decimal("5")})

    def test_empty(self):
        self.assertEqual(balance.balances([]), {})
        self.assertEqual(balance.total([]), Decimal("0"))

    def test_total(self):
        self.assertEqual(balance.total([tx("cash", Decimal("10")), tx("bank", Decimal("-4"))]), Decimal("6"))

    def test_total_has_no_float_precision_loss(self):
        result = balance.total([tx("cash", Decimal("0.1")), tx("cash", Decimal("0.2"))])
        self.assertEqual(result, Decimal("0.3"))

    def test_balances_for_month(self):
        transactions = [
            tx("cash", Decimal("10"), date="2026-08-01"),
            tx("cash", Decimal("5"), date="2026-08-15"),
            tx("bank", Decimal("3"), date="2026-08-20"),
            tx("cash", Decimal("100"), date="2026-09-01"),
        ]
        result = balance.balances_for_month(transactions, "2026-08")
        self.assertEqual(result, {"cash": Decimal("15"), "bank": Decimal("3")})

    def test_balances_for_month_no_matches(self):
        self.assertEqual(balance.balances_for_month([tx("cash", Decimal("10"))], "2026-01"), {})


if __name__ == "__main__":
    unittest.main()
