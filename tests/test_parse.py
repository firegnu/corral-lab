import unittest
from decimal import Decimal

from ledger import parse


class ParseTest(unittest.TestCase):
    def test_header_is_skipped(self):
        txs = parse.parse_lines(["date,account,amount,memo", "2026-08-01,cash,12.50,coffee"])
        self.assertEqual(txs, [parse.Transaction("2026-08-01", "cash", Decimal("12.50"), "coffee")])

    def test_amount_is_decimal(self):
        [tx] = parse.parse_lines(["2026-08-01,cash,12.50,coffee"])
        self.assertIsInstance(tx.amount, Decimal)

    def test_amount_has_no_float_precision_loss(self):
        [tx] = parse.parse_lines(["2026-08-01,cash,0.1"])
        self.assertEqual(tx.amount, Decimal("0.1"))

    def test_memo_is_optional(self):
        [tx] = parse.parse_lines(["2026-08-01,rent,1800"])
        self.assertEqual(tx.memo, "")
        self.assertEqual(tx.amount, Decimal("1800"))

    def test_invalid_amount_raises_value_error(self):
        with self.assertRaises(ValueError):
            parse.parse_lines(["2026-08-01,cash,not-a-number"])

    def test_cells_are_stripped(self):
        [tx] = parse.parse_lines(["2026-08-01 , bank , -3.25 , x "])
        self.assertEqual((tx.account, tx.amount, tx.memo), ("bank", Decimal("-3.25"), "x"))

    def test_too_few_columns_raises(self):
        with self.assertRaises(ValueError):
            parse.parse_lines(["2026-08-01,cash"])

    def test_blank_and_whitespace_lines_are_skipped(self):
        txs = parse.parse_lines([
            "date,account,amount,memo",
            "",
            "2026-08-01,cash,12.50,coffee",
            "   ",
            "2026-08-02,bank,-3.25,x",
            "\n",
        ])
        self.assertEqual(txs, [
            parse.Transaction("2026-08-01", "cash", Decimal("12.50"), "coffee"),
            parse.Transaction("2026-08-02", "bank", Decimal("-3.25"), "x"),
        ])

    def test_comma_only_rows_are_skipped(self):
        txs = parse.parse_lines([
            "date,account,amount,memo",
            ",,",
            " , , ",
            "2026-08-01,cash,12.50,coffee",
        ])
        self.assertEqual(txs, [parse.Transaction("2026-08-01", "cash", Decimal("12.50"), "coffee")])

    def test_header_is_recognized_after_leading_blank_lines(self):
        txs = parse.parse_lines([
            "",
            "   ",
            "date,account,amount,memo",
            "2026-08-01,cash,12.50,coffee",
        ])
        self.assertEqual(txs, [parse.Transaction("2026-08-01", "cash", Decimal("12.50"), "coffee")])


if __name__ == "__main__":
    unittest.main()
