import sqlite3
import pandas as pd

DB = "db/nifty100.db"

conn = sqlite3.connect(DB)

# Latest financial ratios
ratios = pd.read_sql_query("""
SELECT *
FROM financial_ratios r
WHERE year = (
    SELECT MAX(year)
    FROM financial_ratios f
    WHERE f.company_id=r.company_id
      AND f.year!='TTM'
)
""", conn)

# Peer groups
peer = pd.read_sql_query("""
SELECT *
FROM peer_groups
""", conn)

# Company names
companies = pd.read_sql_query("""
SELECT id, company_name
FROM companies
""", conn)

df = ratios.merge(
    peer,
    on="company_id",
    how="left"
)

metrics = [
    "return_on_equity_pct",
    "return_on_capital_employed_pct",
    "net_profit_margin_pct",
    "debt_to_equity",
    "free_cash_flow_cr",
    "pat_cagr_5yr",
    "revenue_cagr_5yr",
    "eps_cagr_5yr",
    "interest_coverage",
    "asset_turnover",
]

records = []

for group_name, group in df.groupby("peer_group_name", dropna=False):

    if pd.isna(group_name):
        continue

    for metric in metrics:

        temp = group[["company_id", "year", metric]].copy()

        temp = temp.dropna()

        if len(temp) == 0:
            continue

        ascending = metric == "debt_to_equity"

        temp["percentile_rank"] = (
            temp[metric]
            .rank(method="average", pct=True, ascending=ascending)
        )

        if metric == "debt_to_equity":
            temp["percentile_rank"] = 1 - temp["percentile_rank"]

        temp["peer_group_name"] = group_name
        temp["metric"] = metric

        records.append(
            temp[
                [
                    "company_id",
                    "peer_group_name",
                    "metric",
                    metric,
                    "percentile_rank",
                    "year",
                ]
            ].rename(columns={metric: "value"})
        )

peer_percentiles = pd.concat(records, ignore_index=True)

peer_percentiles.to_sql(
    "peer_percentiles",
    conn,
    if_exists="replace",
    index=False,
)

print(peer_percentiles.head())

print()

print("Rows:", len(peer_percentiles))

print("Peer Groups:", peer_percentiles.peer_group_name.nunique())

conn.close()