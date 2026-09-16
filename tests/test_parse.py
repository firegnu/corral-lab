import unittest

from ledger import parse


class ParseTest(unittest.TestCase):
    def test_header_is_skipped(self):
        txs = parse.parse_lines(["date,account,amount,memo", "2026-08-01,cash,12.50,coffee"])
        self.assertEqual(txs, [parse.Transaction("2026-08-01", "cash", 12.5, "coffee")])

    def test_memo_is_optional(self):
        [tx] = parse.parse_lines(["2026-08-01,rent,1800"])
        self.assertEqual(tx.memo, "")

    def test_cells_are_stripped(self):
        [tx] = parse.parse_lines(["2026-08-01 , bank , -3.25 , x "])
        self.assertEqual((tx.account, tx.amount, tx.memo), ("bank", -3.25, "x"))

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
            parse.Transaction("2026-08-01", "cash", 12.5, "coffee"),
            parse.Transaction("2026-08-02", "bank", -3.25, "x"),
        ])


if __name__ == "__main__":
    unittest.main()
