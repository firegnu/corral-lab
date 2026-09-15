import contextlib
import io
import os
import unittest

from ledger import cli, report

SAMPLE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample", "transactions.csv")


class ReportTest(unittest.TestCase):
    def test_sorted_with_total(self):
        lines = report.format_report({"rent": 1800.0, "bank": -12.5}).splitlines()
        self.assertEqual([line.split()[0] for line in lines], ["account", "bank", "rent", "TOTAL"])
        self.assertTrue(lines[-1].endswith("1,787.50"))

    def test_thousands_separator(self):
        self.assertEqual(report.format_amount(1234567.891), "1,234,567.89")


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

    def test_balance_on_sample(self):
        self.assertEqual(self.run_cli("balance", SAMPLE, "rent").strip(), "1,800.00")


if __name__ == "__main__":
    unittest.main()
