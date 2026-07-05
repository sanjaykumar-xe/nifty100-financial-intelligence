import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

DB = Path("db/nifty100.db")
OUTPUT_DIR = Path("reports/radar_charts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB)

query = """
SELECT
    r.company_id,
    c.company_name,
    p.peer_group_name,
    r.return_on_equity_pct,
    r.return_on_capital_employed_pct,
    r.net_profit_margin_pct,
    r.debt_to_equity,
    r.free_cash_flow_cr,
    r.pat_cagr_5yr,
    r.revenue_cagr_5yr,
    r.composite_quality_score
FROM financial_ratios r
LEFT JOIN companies c ON r.company_id = c.id
LEFT JOIN peer_groups p ON r.company_id = p.company_id
WHERE r.year = (
    SELECT MAX(year)
    FROM financial_ratios fr
    WHERE fr.company_id = r.company_id
      AND fr.year != 'TTM'
)
"""

df = pd.read_sql_query(query, conn)
conn.close()

metrics = [
    "return_on_equity_pct",
    "return_on_capital_employed_pct",
    "net_profit_margin_pct",
    "debt_to_equity",
    "free_cash_flow_cr",
    "pat_cagr_5yr",
    "revenue_cagr_5yr",
    "composite_quality_score",
]

labels = [
    "ROE",
    "ROCE",
    "NPM",
    "D/E",
    "FCF",
    "PAT CAGR",
    "Revenue CAGR",
    "Score",
]

for col in metrics:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Convert D/E so lower debt becomes better score
df["debt_to_equity"] = df["debt_to_equity"].max() - df["debt_to_equity"]

# Normalize metrics to 0–100
for col in metrics:
    min_val = df[col].min()
    max_val = df[col].max()

    if pd.isna(min_val) or pd.isna(max_val) or max_val == min_val:
        df[col + "_score"] = 50
    else:
        df[col + "_score"] = ((df[col] - min_val) / (max_val - min_val)) * 100

score_cols = [col + "_score" for col in metrics]

for _, row in df.iterrows():
    company_id = row["company_id"]
    peer_group = row["peer_group_name"]

    company_values = row[score_cols].fillna(0).astype(float).tolist()

    if pd.notna(peer_group):
        peer_avg = (
            df[df["peer_group_name"] == peer_group][score_cols]
            .mean()
            .fillna(0)
            .astype(float)
            .tolist()
        )
    else:
        peer_avg = df[score_cols].mean().fillna(0).astype(float).tolist()

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()

    company_values += company_values[:1]
    peer_avg += peer_avg[:1]
    angles += angles[:1]

    fig = plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, polar=True)

    ax.plot(angles, company_values, linewidth=2, label=company_id)
    ax.fill(angles, company_values, alpha=0.25)

    ax.plot(angles, peer_avg, linewidth=2, linestyle="dashed", label="Peer Avg")

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_yticklabels([])
    ax.set_title(f"{company_id} Radar Chart", fontsize=14)
    ax.legend(loc="upper right", bbox_to_anchor=(1.2, 1.1))

    filename = OUTPUT_DIR / f"{company_id}_radar.png"
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()

print(f"Radar charts saved to {OUTPUT_DIR}")
print(f"Charts generated: {len(df)}")