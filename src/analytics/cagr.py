def calculate_cagr(start_value, end_value, years):
    """
    Calculate CAGR with edge-case flags.
    Returns: (value, flag)
    """

    if years <= 0:
        return None, "INSUFFICIENT"

    if start_value is None or end_value is None:
        return None, "INSUFFICIENT"

    if start_value == 0:
        return None, "ZERO_BASE"

    if start_value > 0 and end_value > 0:
        cagr = ((end_value / start_value) ** (1 / years) - 1) * 100
        return cagr, "NORMAL"

    if start_value > 0 and end_value < 0:
        return None, "DECLINE_TO_LOSS"

    if start_value < 0 and end_value > 0:
        return None, "TURNAROUND"

    if start_value < 0 and end_value < 0:
        return None, "BOTH_NEGATIVE"

    return None, "UNDEFINED"


def compute_period_cagr(df, value_column, company_id, years):
    """
    Compute CAGR for a company using a dataframe with year and value column.
    """

    company_data = df[df["company_id"] == company_id].copy()

    if len(company_data) < years + 1:
        return None, "INSUFFICIENT"

    company_data = company_data.sort_values("year")

    start_value = company_data.iloc[-(years + 1)][value_column]
    end_value = company_data.iloc[-1][value_column]

    return calculate_cagr(start_value, end_value, years)