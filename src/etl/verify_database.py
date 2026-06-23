import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("db/nifty100.db")
OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

tables = [
    "companies",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "analysis",
    "documents",
    "prosandcons",
    "sectors",
    "stock_prices",
    "market_cap",
    "financial_ratios",
]

conn = sqlite3.connect(DB_PATH)

results = []

for table in tables:
    count = pd.read_sql_query(f"SELECT COUNT(*) AS row_count FROM {table}", conn)
    row_count = int(count["row_count"].iloc[0])

    results.append({
        "table": table,
        "row_count": row_count
    })

    print(f"{table}: {row_count}")

fk_check = pd.read_sql_query("PRAGMA foreign_key_check;", conn)
fk_check.to_csv(OUTPUT / "foreign_key_check.csv", index=False)

pd.DataFrame(results).to_csv(OUTPUT / "database_row_counts.csv", index=False)

conn.close()

print("\nDatabase verification completed.")
print("Saved: output/database_row_counts.csv")
print("Saved: output/foreign_key_check.csv")
print(f"Foreign key errors: {len(fk_check)}")