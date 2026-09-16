"""命令行：python3 -m ledger report <文件> / python3 -m ledger balance <文件> <账户> / python3 -m ledger month <文件> <YYYY-MM>"""
import argparse
from decimal import Decimal

from ledger import balance, parse, report


def main(argv=None):
    p = argparse.ArgumentParser(prog="ledger")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("report")
    r.add_argument("file")
    b = sub.add_parser("balance")
    b.add_argument("file")
    b.add_argument("account")
    m = sub.add_parser("month")
    m.add_argument("file")
    m.add_argument("month")
    args = p.parse_args(argv)

    transactions = parse.parse_file(args.file)
    if args.cmd == "report":
        print(report.format_report(balance.balances(transactions)))
    elif args.cmd == "balance":
        totals = balance.balances(transactions)
        print(report.format_amount(totals.get(args.account, Decimal("0"))))
    else:
        print(report.format_report(balance.balances_for_month(transactions, args.month)))
    return 0
