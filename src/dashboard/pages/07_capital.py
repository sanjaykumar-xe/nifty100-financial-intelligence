import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.title("🗺️ Capital Allocation Map")

conn = sqlite3.connect("db/nifty100.db")

companies = pd.read_sql("""
SELECT id, company_name
FROM companies
""", conn)

ratios = pd.read_sql("""
SELECT *
FROM financial_ratios
""", conn)

market = pd.read_sql("""
SELECT *
FROM market_cap
""", conn)

conn.close()

ratios = (
    ratios
    .sort_values("year")
    .groupby("company_id")
    .tail(1)
)

market = (
    market
    .sort_values("year")
    .groupby("company_id")
    .tail(1)
)

df = ratios.merge(
    companies,
    left_on="company_id",
    right_on="id",
    how="left"
)

df = df.merge(
    market[["company_id", "market_cap_crore"]],
    on="company_id",
    how="left"
)

df["market_cap_crore"] = pd.to_numeric(
    df["market_cap_crore"],
    errors="coerce"
).fillna(0)

def classify(row):

    roe = row.get("return_on_equity_pct", 0)
    de = row.get("debt_to_equity", 0)
    fcf = row.get("free_cash_flow_cr", 0)

    if roe > 20 and de < 1:
        return "Compounders"

    elif fcf > 0 and roe > 15:
        return "Cash Generators"

    elif de > 2:
        return "Highly Leveraged"

    elif roe < 10:
        return "Turnaround"

    elif fcf < 0:
        return "Growth Investing"

    else:
        return "Stable"

df["allocation_pattern"] = df.apply(
    classify,
    axis=1
)

fig = px.treemap(
    df,
    path=["allocation_pattern", "company_name"],
    values="market_cap_crore",
    title="Capital Allocation Patterns"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

pattern = st.selectbox(
    "Select Pattern",
    sorted(df["allocation_pattern"].unique())
)

result = df[
    df["allocation_pattern"] == pattern
][[
    "company_id",
    "company_name",
    "return_on_equity_pct",
    "debt_to_equity",
    "free_cash_flow_cr"
]]

st.dataframe(
    result,
    use_container_width=True
)