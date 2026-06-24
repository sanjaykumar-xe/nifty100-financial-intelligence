import re

import re

def normalize_year(year):
    if year is None:
        return None

    year = str(year).strip()

    # 4-digit year
    match = re.search(r"(20\d{2})", year)
    if match:
        return int(match.group(1))

    # Month-year format: Mar-24, Dec-16 etc.
    match = re.search(r"[A-Za-z]{3}[- ](\d{2})$", year)
    if match:
        yy = int(match.group(1))
        return 2000 + yy

    # Year range format: 2014/15
    match = re.search(r"(20\d{2})/\d{2}", year)
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