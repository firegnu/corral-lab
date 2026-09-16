"""读交易记录 CSV。列：date,account,amount,memo（memo 可省略），第一行可以是表头。"""
import csv
from dataclasses import dataclass
from decimal import Decimal

HEADER = ["date", "account", "amount", "memo"]


@dataclass
class Transaction:
    date: str
    account: str
    amount: Decimal
    memo: str = ""


def parse_row(row):
    if len(row) < 3:
        raise ValueError(f"expected at least 3 columns, got {len(row)}: {row!r}")
    date, account, amount = (cell.strip() for cell in row[:3])
    memo = row[3].strip() if len(row) > 3 else ""
    return Transaction(date, account, Decimal(amount), memo)


def parse_lines(lines):
    transactions = []
    seen_row = False
    for row in csv.reader(lines):
        if not any(cell.strip() for cell in row):
            continue
        if not seen_row:
            seen_row = True
            if [cell.strip().lower() for cell in row[:4]] == HEADER[:len(row[:4])]:
                continue
        transactions.append(parse_row(row))
    return transactions


def parse_file(path):
    with open(path, newline="", encoding="utf-8") as f:
        return parse_lines(f)
