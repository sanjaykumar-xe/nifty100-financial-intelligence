import sqlite3
from pathlib import Path
import pandas as pd

DB = Path("db/nifty100.db")
OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

conn = sqlite3.connect(DB)

query = """
SELECT
    c.id AS company_id,
    c.company_name,
    c.roce_percentage AS source_roce,
    c.roe_percentage AS source_roe,
    s.broad_sector,
    r.year,
    r.return_on_capital_employed_pct AS computed_roce,
    r.return_on_equity_pct AS computed_roe,
    r.debt_to_equity,
    r.high_leverage_flag
FROM companies c
LEFT JOIN sectors s ON c.id = s.company_id
LEFT JOIN financial_ratios r
ON c.id = r.company_id
AND r.year = (
    SELECT MAX(year)
    FROM financial_ratios f
    WHERE f.company_id = c.id
)
"""

df = pd.read_sql_query(query, conn)

log_lines = []

for _, row in df.iterrows():
    company = row["company_id"]
    year = row["year"]
    sector = row["broad_sector"]

    try:
        source_roce = float(row["source_roce"]) if pd.notna(row["source_roce"]) else None
        computed_roce = float(row["computed_roce"]) if pd.notna(row["computed_roce"]) else None
    except Exception:
        source_roce = None
        computed_roce = None

    try:
        source_roe = float(row["source_roe"]) if pd.notna(row["source_roe"]) else None
        computed_roe = float(row["computed_roe"]) if pd.notna(row["computed_roe"]) else None
    except Exception:
        source_roe = None
        computed_roe = None

    if source_roce is not None and computed_roce is not None:
        diff = abs(source_roce - computed_roce)
        if diff > 5:
            log_lines.append(
                f"{company} | {year} | ROCE anomaly | Source={source_roce:.2f}, Computed={computed_roce:.2f}, Diff={diff:.2f} | Category=Formula discrepancy / version difference"
            )

    if source_roe is not None and computed_roe is not None:
        diff = abs(source_roe - computed_roe)
        if diff > 5:
            log_lines.append(
                f"{company} | {year} | ROE anomaly | Source={source_roe:.2f}, Computed={computed_roe:.2f}, Diff={diff:.2f} | Category=Data source issue / formula discrepancy"
            )

    if sector == "Financials":
        log_lines.append(
            f"{company} | {year} | Financials carve-out | D/E warning suppressed because high leverage is structurally normal in Financials | Category=Bank/NBFC carve-out"
        )

if not log_lines:
    log_lines.append("No major ratio edge cases found.")

with open(OUTPUT / "ratio_edge_cases.log", "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))

conn.close()

print("Saved output/ratio_edge_cases.log")
print("Total edge cases logged:", len(log_lines))