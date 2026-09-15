"""命令行：python3 -m ledger report <文件> / python3 -m ledger balance <文件> <账户>"""
import argparse

from ledger import balance, parse, report


def main(argv=None):
    p = argparse.ArgumentParser(prog="ledger")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("report")
    r.add_argument("file")
    b = sub.add_parser("balance")
    b.add_argument("file")
    b.add_argument("account")
    args = p.parse_args(argv)

    transactions = parse.parse_file(args.file)
    totals = balance.balances(transactions)
    if args.cmd == "report":
        print(report.format_report(totals))
    else:
        print(report.format_amount(totals.get(args.account, 0.0)))
    return 0
