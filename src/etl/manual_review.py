import sqlite3
import pandas as pd
import random
from pathlib import Path

DB = Path("db/nifty100.db")
OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

conn = sqlite3.connect(DB)

# Review 5 random companies
companies = pd.read_sql("SELECT id, company_name FROM companies", conn)

sample = companies.sample(5, random_state=42)

print("\n===== RANDOM COMPANY REVIEW =====")

for _, row in sample.iterrows():
    cid = row["id"]

    years = pd.read_sql(
        f"""
        SELECT COUNT(*) AS total_years
        FROM profitandloss
        WHERE company_id='{cid}'
        """,
        conn,
    )

    print(f"{cid:<15} {row['company_name']:<35} Years = {years.iloc[0,0]}")

# Companies having less than 5 years
coverage = pd.read_sql("""
SELECT company_id,
COUNT(*) AS years_available
FROM profitandloss
GROUP BY company_id
HAVING COUNT(*) < 5
ORDER BY years_available;
""", conn)

coverage.to_csv(
    OUTPUT / "companies_less_than_5_years.csv",
    index=False
)

print("\nCompanies with <5 years saved.")

conn.close()