"""按账户汇总金额。"""
from collections import defaultdict
from decimal import Decimal


def balances(transactions):
    totals = defaultdict(Decimal)
    for t in transactions:
        totals[t.account] += t.amount
    return dict(totals)


def total(transactions):
    return sum((t.amount for t in transactions), Decimal("0"))


def balances_for_month(transactions, month):
    return balances(t for t in transactions if t.date.startswith(month))
