import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go

st.title("👥 Peer Comparison")

# --------------------------
# Load Data
# --------------------------

conn = sqlite3.connect("db/nifty100.db")

peer_groups = pd.read_sql(
    "SELECT * FROM peer_groups",
    conn
)

ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

companies = pd.read_sql(
    """
    SELECT
        id,
        company_name
    FROM companies
    """,
    conn
)

conn.close()

# --------------------------
# Latest financial record
# --------------------------

ratios = ratios[ratios["year"] != "TTM"]
ratios = (
    ratios
    .sort_values("year")
    .groupby("company_id")
    .tail(1)
)

# --------------------------
# Peer Group Selection
# --------------------------

group_list = sorted(
    peer_groups["peer_group_name"].unique()
)

selected_group = st.selectbox(
    "Select Peer Group",
    group_list
)

peer_companies = peer_groups[
    peer_groups["peer_group_name"] == selected_group
]["company_id"].tolist()

selected_company = st.selectbox(
    "Select Company",
    peer_companies
)

peer_data = ratios[
    ratios["company_id"].isin(peer_companies)
].copy()

# --------------------------
# Metrics for Radar Chart
# --------------------------

metrics = [
    "return_on_equity_pct",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover",
    "free_cash_flow_cr",
    "return_on_capital_employed_pct",
    "return_on_assets_pct"
]

for col in metrics:
    if col in peer_data.columns:
        peer_data[col] = pd.to_numeric(
            peer_data[col],
            errors="coerce"
        )

peer_data[metrics] = peer_data[metrics].fillna(0)

peer_avg = peer_data[metrics].mean()

company_row = peer_data[
    peer_data["company_id"] == selected_company
]

if company_row.empty:
    st.warning("No data available for selected company.")
    st.stop()

company_row = company_row.iloc[0]

company_values = [
    company_row[m]
    for m in metrics
]

peer_values = [
    peer_avg[m]
    for m in metrics
]

# --------------------------
# Radar Chart
# --------------------------

fig = go.Figure()

fig.add_trace(
    go.Scatterpolar(
        r=company_values,
        theta=metrics,
        fill="toself",
        name=selected_company
    )
)

fig.add_trace(
    go.Scatterpolar(
        r=peer_values,
        theta=metrics,
        fill="toself",
        name="Peer Average"
    )
)

fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True
        )
    ),
    showlegend=True,
    height=600
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------
# Peer Table
# --------------------------

st.subheader("Peer Comparison Table")

display = peer_data.merge(
    companies,
    left_on="company_id",
    right_on="id",
    how="left"
)

cols = [
    "company_id",
    "company_name",
    "return_on_equity_pct",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover",
    "free_cash_flow_cr",
    "return_on_capital_employed_pct",
    "return_on_assets_pct",
    "composite_quality_score"
]

display = display.fillna("N/A")

st.dataframe(
    display[cols],
    use_container_width=True
)