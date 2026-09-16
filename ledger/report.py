"""把余额排成文字报表。"""
from decimal import Decimal, ROUND_HALF_UP

CENTS = Decimal("0.01")


def format_amount(amount):
    quantized = amount.quantize(CENTS, rounding=ROUND_HALF_UP)
    if quantized == 0:
        quantized = abs(quantized)
    return f"{quantized:,}"


def format_report(balances):
    width = max([len("account")] + [len(a) for a in balances])
    lines = [f"{'account':<{width}}  {'amount':>12}"]
    for account in sorted(balances):
        lines.append(f"{account:<{width}}  {format_amount(balances[account]):>12}")
    total = sum(balances.values(), Decimal("0"))
    lines.append(f"{'TOTAL':<{width}}  {format_amount(total):>12}")
    return "\n".join(lines)
