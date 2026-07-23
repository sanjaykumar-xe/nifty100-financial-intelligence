import sqlite3
import pandas as pd
import re
from pathlib import Path

DB = "db/nifty100.db"

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

conn = sqlite3.connect(DB)

analysis = pd.read_sql(
    """
    SELECT
        company_id,
        compounded_sales_growth,
        compounded_profit_growth,
        stock_price_cagr,
        roe
    FROM analysis
    """,
    conn,
)

pattern = re.compile(r"(\d+)\s*Years?:?\s*([-]?\d+\.?\d*)%")

parsed_rows = []
failed_rows = []

metrics = [
    "compounded_sales_growth",
    "compounded_profit_growth",
    "stock_price_cagr",
    "roe",
]

for _, row in analysis.iterrows():

    company = row["company_id"]

    for metric in metrics:

        value = str(row[metric])

        match = pattern.search(value)

        if match:

            parsed_rows.append(
                {
                    "company_id": company,
                    "metric_type": metric,
                    "period_years": int(match.group(1)),
                    "value_pct": float(match.group(2)),
                }
            )

        else:

            failed_rows.append(
                {
                    "company_id": company,
                    "metric_type": metric,
                    "raw_text": value,
                }
            )

parsed_df = pd.DataFrame(parsed_rows)
failed_df = pd.DataFrame(failed_rows)

parsed_df.to_csv(
    OUTPUT_DIR / "analysis_parsed.csv",
    index=False,
)

failed_df.to_csv(
    OUTPUT_DIR / "parse_failures.csv",
    index=False,
)

print("Parsed rows:", len(parsed_df))
print("Failed rows:", len(failed_df))