import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.title("🏠 Home Dashboard")

# -----------------------------
# Load Data
# -----------------------------
conn = sqlite3.connect("db/nifty100.db")

companies = pd.read_sql_query(
    "SELECT * FROM companies",
    conn
)

ratios = pd.read_sql_query(
    """
    SELECT *
    FROM financial_ratios
    """,
    conn
)

sectors = pd.read_sql_query(
    """
    SELECT *
    FROM sectors
    """,
    conn
)

conn.close()

# -----------------------------
# KPI Metrics
# -----------------------------
avg_roe = round(
    ratios["return_on_equity_pct"].median(),
    2
)

median_roe = round(
    ratios["return_on_equity_pct"].median(),
    2
)

median_de = round(
    ratios["debt_to_equity"].median(),
    2
)

company_count = companies["id"].nunique()

# -----------------------------
# Metrics Row
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Average ROE", avg_roe)
col2.metric("Median ROE", median_roe)
col3.metric("Median D/E", median_de)
col4.metric("Companies", company_count)

st.divider()

# -----------------------------
# Sector Distribution
# -----------------------------
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