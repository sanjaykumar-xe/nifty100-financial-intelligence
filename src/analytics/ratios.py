def safe_divide(numerator, denominator):
    if denominator is None or denominator == 0:
        return None
    try:
        return (numerator / denominator) * 100
    except Exception:
        return None


def net_profit_margin(net_profit, sales):
    if sales == 0:
        return None
    return safe_divide(net_profit, sales)


def operating_profit_margin(operating_profit, sales):
    if sales == 0:
        return None
    return safe_divide(operating_profit, sales)


def opm_mismatch_flag(computed_opm, source_opm, tolerance=1):
    if computed_opm is None or source_opm is None:
        return False
    return abs(computed_opm - source_opm) > tolerance


def return_on_equity(net_profit, equity_capital, reserves):
    equity = equity_capital + reserves
    if equity <= 0:
        return None
    return safe_divide(net_profit, equity)


def return_on_capital_employed(operating_profit, depreciation, equity_capital, reserves, borrowings):
    ebit = operating_profit - depreciation
    capital_employed = equity_capital + reserves + borrowings
    if capital_employed <= 0:
        return None
    return safe_divide(ebit, capital_employed)


def return_on_assets(net_profit, total_assets):
    if total_assets == 0:
        return None
    return safe_divide(net_profit, total_assets)
def debt_to_equity(borrowings, equity_capital, reserves):
    equity = equity_capital + reserves

    if borrowings == 0:
        return 0

    if equity <= 0:
        return None

    return borrowings / equity


def high_leverage_flag(de_ratio, broad_sector):
    if de_ratio is None:
        return False

    if broad_sector == "Financials":
        return False

    return de_ratio > 5


def interest_coverage_ratio(operating_profit, other_income, interest):
    if interest == 0:
        return None

    return (operating_profit + other_income) / interest


def icr_label(icr):
    if icr is None:
        return "Debt Free"

    return "Normal"


def icr_warning_flag(icr):
    if icr is None:
        return False

    return icr < 1.5


def net_debt(borrowings, investments):
    return borrowings - investments


def asset_turnover(sales, total_assets):
    if total_assets == 0:
        return None

    return sales / total_assets