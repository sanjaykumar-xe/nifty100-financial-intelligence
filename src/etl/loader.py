from pathlib import Path
import pandas as pd

RAW_DATA = Path("data/raw")


def load_excel(filename):
    """
    Load an Excel file from the raw data folder.
    """
    filepath = RAW_DATA / filename

    df = pd.read_excel(filepath)

    print(f"Loaded {filename}: {len(df)} rows")

    return df


if __name__ == "__main__":

    files = [
        "companies.xlsx",
        "profitandloss.xlsx",
        "balancesheet.xlsx",
        "cashflow.xlsx",
        "analysis.xlsx",
        "documents.xlsx",
        "prosandcons.xlsx",
        "financial_ratios.xlsx",
        "market_cap.xlsx",
        "peer_groups.xlsx",
        "sectors.xlsx",
        "stock_prices.xlsx",
    ]

    for file in files:
        load_excel(file)