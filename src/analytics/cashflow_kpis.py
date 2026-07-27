"""
Reusable Cashflow KPI functions
"""

def free_cash_flow(cfo, capex):
    """
    Free Cash Flow = CFO + Investing CAPEX
    (CAPEX is usually negative)
    """
    return cfo + capex


def cfo_quality_score(cfo, net_profit):
    """
    Compare CFO with Net Profit
    """

    if net_profit == 0:
        return "Accrual Risk"

    ratio = (cfo / net_profit) * 100

    if ratio >= 100:
        return "High Quality"

    elif ratio >= 50:
        return "Moderate"

    else:
        return "Accrual Risk"


def capex_intensity(capex, revenue):
    """
    CAPEX Intensity %
    """

    if revenue == 0:
        return 0, "Unknown"

    intensity = abs(capex) / revenue * 100

    if intensity < 5:
        label = "Asset Light"

    elif intensity < 10:
        label = "Balanced"

    else:
        label = "Capital Intensive"

    return round(intensity, 2), label


def fcf_conversion_rate(fcf, cfo):
    """
    FCF Conversion %
    """

    if cfo == 0:
        return 0

    return round((fcf / cfo) * 100, 2)


def capital_allocation_pattern(cfo, investing_cf, financing_cf):
    """
    Simple capital allocation classifier
    """

    if cfo > 0 and investing_cf < 0 and financing_cf < 0:
        return "Reinvestor"

    elif cfo < 0 and financing_cf > 0:
        return "Growth Funded by Debt"

    elif cfo > 0 and financing_cf < 0:
        return "Cash Generator"

    else:
        return "Stable"