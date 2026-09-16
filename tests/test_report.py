import contextlib
import io
import os
import unittest
from decimal import Decimal

from ledger import cli, report

SAMPLE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample", "transactions.csv")


class ReportTest(unittest.TestCase):
    def test_sorted_with_total(self):
        lines = report.format_report({"rent": Decimal("1800.0"), "bank": Decimal("-12.5")}).splitlines()
        self.assertEqual([line.split()[0] for line in lines], ["account", "bank", "rent", "TOTAL"])
        self.assertTrue(lines[-1].endswith("1,787.50"))

    def test_thousands_separator(self):
        self.assertEqual(report.format_amount(Decimal("1234567.891")), "1,234,567.89")

    def test_negative_zero_is_normalized(self):
        self.assertEqual(report.format_amount(Decimal("-0.00")), "0.00")

    def test_small_negative_rounds_to_positive_zero(self):
        self.assertEqual(report.format_amount(Decimal("-0.001")), "0.00")

    def test_no_float_precision_artifacts(self):
        self.assertEqual(report.format_amount(Decimal("0.1") + Decimal("0.2")), "0.30")

    def test_amount_without_decimal_point(self):
        self.assertEqual(report.format_amount(Decimal("1800")), "1,800.00")

    def test_large_realistic_amount(self):
        self.assertEqual(report.format_amount(Decimal("999999999.99")), "999,999,999.99")

    def test_format_report_empty_total_has_no_negative_zero(self):
        lines = report.format_report({}).splitlines()
        self.assertTrue(lines[-1].endswith("0.00"))
        self.assertNotIn("-0.00", lines[-1])


class CliTest(unittest.TestCase):
    def run_cli(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(cli.main(list(argv)), 0)
        return out.getvalue()

    def test_report_on_sample(self):
        text = self.run_cli("report", SAMPLE)
        self.assertIn("food:groceries", text)
        self.assertIn("TOTAL", text)

    def test_report_with_account_prefix(self):
        text = self.run_cli("report", SAMPLE, "--account-prefix", "food:")
        lines = text.splitlines()
        amounts = {account.strip(): amount for account, amount in (line.rsplit(maxsplit=1) for line in lines[1:])}
        self.assertEqual(amounts, {
            "food:dining": "0.30",
            "food:groceries": "178.55",
            "TOTAL": "178.85",
        })

    def test_report_with_account_prefix_no_matches(self):
        text = self.run_cli("report", SAMPLE, "--account-prefix", "zzz")
        lines = text.strip().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[-1].split()[-1], "0.00")

    def test_balance_on_sample(self):
        self.assertEqual(self.run_cli("balance", SAMPLE, "rent").strip(), "1,800.00")

    def test_month_on_sample(self):
        text = self.run_cli("month", SAMPLE, "2026-08")
        self.assertIn("food:dining", text)
        self.assertIn("TOTAL", text)

    def test_month_excludes_other_months(self):
        text = self.run_cli("month", SAMPLE, "2026-09")
        self.assertNotIn("food:dining", text)
        self.assertIn("food:groceries", text)

    def test_month_on_sample_exact_amounts(self):
        lines = self.run_cli("month", SAMPLE, "2026-08").splitlines()
        amounts = {account.strip(): amount for account, amount in (line.rsplit(maxsplit=1) for line in lines[1:])}
        self.assertEqual(amounts, {
            "bank": "3,200.00",
            "cash": "-86.70",
            "food:dining": "0.30",
            "food:groceries": "86.40",
            "rent": "1,800.00",
            "salary": "-5,000.00",
            "TOTAL": "0.00",
        })

    def test_month_with_no_transactions(self):
        text = self.run_cli("month", SAMPLE, "2026-01")
        self.assertEqual(text.strip().splitlines()[-1].split()[-1], "0.00")
        self.assertNotIn("food", text)


if __name__ == "__main__":
    unittest.main()
