import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.title("🏭 Sector Analysis")

# -------------------------
# Load Data
# -------------------------

conn = sqlite3.connect("db/nifty100.db")

companies = pd.read_sql(
    """
    SELECT *
    FROM companies
    """,
    conn
)

sectors = pd.read_sql(
    """
    SELECT *
    FROM sectors
    """,
    conn
)

ratios = pd.read_sql(
    """
    SELECT *
    FROM financial_ratios
    """,
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
# Latest financial data
# -------------------------

ratios = ratios[ratios["year"] != "TTM"]
ratios = (
    ratios
    .sort_values("year")
    .groupby("company_id")
    .tail(1)
)
# -------------------------
# Merge Data
# -------------------------

df = sectors.merge(
    companies,
    left_on="company_id",
    right_on="id",
    how="left"
)

df = df.merge(
    ratios,
    on="company_id",
    how="left"
)

df = df.merge(
    market,
    on="company_id",
    how="left"
)

# -------------------------
# Numeric Conversion
# -------------------------

numeric_cols = [
    "return_on_equity_pct",
    "market_cap_crore"
]

for col in numeric_cols:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

df = df.fillna(0)

# -------------------------
# Sector Selector
# -------------------------

sector_list = sorted(
    df["broad_sector"].dropna().unique()
)

selected_sector = st.selectbox(
    "Select Sector",
    sector_list
)

sector_df = df[
    df["broad_sector"] == selected_sector
]

# -------------------------
# Bubble Chart
# -------------------------

st.subheader("Revenue vs ROE")

fig = px.scatter(
    sector_df,
    x="market_cap_crore",
    y="return_on_equity_pct",
    size="market_cap_crore",
    color="sub_sector",
    hover_name="company_name",
    title=f"{selected_sector} Companies"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -------------------------
# Sector Median KPIs
# -------------------------

st.subheader("Sector Median Metrics")


med_roe = round(sector_df["return_on_equity_pct"].median(), 2)
med_mcap = round(sector_df["market_cap_crore"].median(), 2)
company_count = len(sector_df)

m1, m2, m3 = st.columns(3)
m1.metric("Median ROE (%)", med_roe)
m2.metric("Median Market Cap (Cr)", f"{med_mcap:,.0f}")
m3.metric("Companies", company_count)



# -------------------------
# Company Table
# -------------------------

st.subheader("Companies")

display_cols = [
    "company_id",
    "company_name",
    "sub_sector",
    "return_on_equity_pct",
    "market_cap_crore"
]

st.dataframe(
    sector_df[display_cols],
    use_container_width=True
)