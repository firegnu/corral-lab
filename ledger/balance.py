"""按账户汇总金额。"""
from collections import defaultdict


def balances(transactions):
    totals = defaultdict(float)
    for t in transactions:
        totals[t.account] += t.amount
    return dict(totals)


def total(transactions):
    return sum(t.amount for t in transactions)


def balances_for_month(transactions, month):
    return balances(t for t in transactions if t.date.startswith(month))
