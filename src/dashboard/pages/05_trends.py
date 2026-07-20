import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.title("📈 Trend Analysis")

# -------------------------
# Load Data
# -------------------------

conn = sqlite3.connect("db/nifty100.db")

companies = pd.read_sql(
    """
    SELECT id, company_name
    FROM companies
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

conn.close()

# -------------------------
# Company Selection
# -------------------------

company_list = companies["id"].tolist()

selected_company = st.selectbox(
    "Select Company",
    company_list
)

company_name = companies.loc[
    companies["id"] == selected_company,
    "company_name"
].values[0]

st.subheader(company_name)

# -------------------------
# Filter Data
# -------------------------

company_data = ratios[
    ratios["company_id"] == selected_company
].copy()

if company_data.empty:
    st.warning("No data available.")
    st.stop()

company_data = company_data.sort_values("year")

# -------------------------
# Metrics Selector
# -------------------------

available_metrics = [
    "return_on_equity_pct",
    "return_on_capital_employed_pct",
    "return_on_assets_pct",
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "debt_to_equity",
    "interest_coverage",
    "free_cash_flow_cr",
    "revenue_cagr_3yr",
    "revenue_cagr_5yr",
    "pat_cagr_3yr",
    "pat_cagr_5yr",
    "eps_cagr_3yr",
    "eps_cagr_5yr",
    "composite_quality_score"
]

selected_metrics = st.multiselect(
    "Select up to 3 Metrics",
    available_metrics,
    default=["return_on_equity_pct"]
)

selected_metrics = selected_metrics[:3]

# -------------------------
# Convert Numeric
# -------------------------

for col in selected_metrics:
    company_data[col] = pd.to_numeric(
        company_data[col],
        errors="coerce"
    )

# -------------------------
# Trend Chart
# -------------------------

if len(selected_metrics) > 0:

    fig = px.line(
        company_data,
        x="year",
        y=selected_metrics,
        markers=True,
        title=f"{company_name} - Multi Metric Trend"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# -------------------------
# YoY Change Table
# -------------------------

st.subheader("Year-over-Year Change (%)")

yoy_df = company_data[["year"] + selected_metrics].copy()

for metric in selected_metrics:
    yoy_df[f"{metric}_YoY_%"] = (
        yoy_df[metric]
        .pct_change()
        * 100
    ).round(2)

st.dataframe(
    yoy_df,
    use_container_width=True
)

# -------------------------
# Raw Data
# -------------------------

with st.expander("View Raw Data"):
    st.dataframe(
        company_data,
        use_container_width=True
    )