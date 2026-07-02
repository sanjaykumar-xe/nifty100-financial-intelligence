def free_cash_flow(operating_activity, investing_activity):
    return operating_activity + investing_activity


def cfo_quality_score(cfo, pat):
    if pat == 0:
        return None

    ratio = cfo / pat

    if ratio > 1:
        return "High Quality"

    if ratio >= 0.5:
        return "Moderate"

    return "Accrual Risk"


def capex_intensity(investing_activity, sales):
    if sales == 0:
        return None

    pct = abs(investing_activity) / sales * 100

    if pct < 3:
        label = "Asset Light"
    elif pct <= 8:
        label = "Moderate"
    else:
        label = "Capital Intensive"

    return pct, label


def fcf_conversion_rate(fcf, operating_profit):
    if operating_profit == 0:
        return None

    return (fcf / operating_profit) * 100


def capital_allocation_pattern(cfo, cfi, cff):
    s1 = "+" if cfo >= 0 else "-"
    s2 = "+" if cfi >= 0 else "-"
    s3 = "+" if cff >= 0 else "-"

    pattern = (s1, s2, s3)

    mapping = {
        ("+", "-", "-"): "Reinvestor",
        ("+", "+", "-"): "Liquidating Assets",
        ("-", "+", "+"): "Distress Signal",
        ("-", "-", "+"): "Growth Funded by Debt",
        ("+", "+", "+"): "Cash Accumulator",
        ("-", "-", "-"): "Pre-Revenue",
        ("+", "-", "+"): "Mixed",
    }

    return mapping.get(pattern, "Unknown")