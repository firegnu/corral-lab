"""把余额排成文字报表。"""


def format_amount(amount):
    return f"{amount:,.2f}"


def format_report(balances):
    width = max([len("account")] + [len(a) for a in balances])
    lines = [f"{'account':<{width}}  {'amount':>12}"]
    for account in sorted(balances):
        lines.append(f"{account:<{width}}  {format_amount(balances[account]):>12}")
    lines.append(f"{'TOTAL':<{width}}  {format_amount(sum(balances.values())):>12}")
    return "\n".join(lines)
