import re

def normalize_year(year):
    """
    Convert year values into a standard integer format.
    Examples:
        '2024' -> 2024
        2024.0 -> 2024
        'FY2024' -> 2024
    """
    if year is None:
        return None

    year = str(year)

    match = re.search(r"(20\d{2})", year)

    if match:
        return int(match.group(1))

    return None


def normalize_ticker(ticker):
    """
    Normalize stock ticker symbols.
    """
    if ticker is None:
        return None

    ticker = str(ticker).strip().upper()

    ticker = ticker.replace(".NS", "")
    ticker = ticker.replace(" ", "")

    return ticker