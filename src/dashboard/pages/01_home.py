import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.title("🏠 Home Dashboard")

# -------------------------
# Load Data
# -------------------------

conn = sqlite3.connect("db/nifty100.db")

companies = pd.read_sql(
    "SELECT * FROM companies",
    conn
)

ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

sectors = pd.read_sql(
    "SELECT * FROM sectors",
    conn
)

market = pd.read_sql(
    """
    SELECT *
    FROM market_cap
    WHERE year='2024'
    """,
    conn
)

conn.close()

# -------------------------
# Year Selector
# -------------------------

years = sorted(
    ratios["year"].astype(str).unique()
)

default_year = "Mar 2024" if "Mar 2024" in years else years[-1]

selected_year = st.sidebar.selectbox(
    "Select Year",
    years,
    index=years.index(default_year)
)

ratios_year = ratios[
    ratios["year"].astype(str) == selected_year
].copy()

# -------------------------
# Merge Market Data
# -------------------------

df = ratios_year.merge(
    market,
    on="company_id",
    how="left"
)

# -------------------------
# Convert Numeric Columns
# -------------------------

numeric_cols = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "composite_quality_score",
    "pe_ratio"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

# -------------------------
# KPI Metrics
# -------------------------

avg_roe = round(
    df["return_on_equity_pct"].mean(),
    2
)

median_pe = round(
    df["pe_ratio"].median(),
    2
)

median_de = round(
    df["debt_to_equity"].median(),
    2
)

median_rev_cagr = round(
    df["revenue_cagr_5yr"].median(),
    2
)

debt_free_count = (
    df["debt_to_equity"] <= 0
).sum()

total_companies = companies["id"].nunique()

# -------------------------
# KPI Tiles
# -------------------------

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("Average ROE", avg_roe)
c2.metric("Median P/E", median_pe)
c3.metric("Median D/E", median_de)
c4.metric("Total Companies", total_companies)
c5.metric("Revenue CAGR 5Y", median_rev_cagr)
c6.metric("Debt Free", debt_free_count)

st.divider()

# -------------------------
# Sector Distribution
# -------------------------

st.subheader("📊 Sector Distribution")

sector_counts = (
    sectors.groupby("broad_sector")
    .size()
    .reset_index(name="count")
)

fig = px.pie(
    sector_counts,
    names="broad_sector",
    values="count",
    hole=0.5,
    title="Sector Distribution"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -------------------------
# Top 5 Quality Companies
# -------------------------

st.subheader("🏆 Top 5 Quality Companies")

top5 = (
    df.dropna(
        subset=["composite_quality_score"]
    )
    .sort_values(
        "composite_quality_score",
        ascending=False
    )
    .head(5)
)

display_top5 = top5[
    [
        "company_id",
        "composite_quality_score",
        "return_on_equity_pct",
        "revenue_cagr_5yr"
    ]
].fillna("N/A")

st.dataframe(
    display_top5,
    use_container_width=True
)

# -------------------------
# Data Summary
# -------------------------

st.subheader("📌 Dataset Summary")

st.write(
    f"Showing financial metrics for **{selected_year}**"
)