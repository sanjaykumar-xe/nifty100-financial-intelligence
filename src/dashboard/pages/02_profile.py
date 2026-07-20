import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import time
_start_time = time.time()
from utils.db import (
    get_companies,
    get_company_profile,
    get_pl
)

st.title("🏢 Company Profile")

companies = get_companies()

ticker = st.selectbox(
    "Select Company",
    companies["id"].sort_values().tolist()
)

company, sector, ratios = get_company_profile(ticker)

if company.empty:
    st.error("Ticker not found — please try another")
    st.stop()

company_row = company.iloc[0]
st.subheader(company_row["company_name"])

col1, col2, col3 = st.columns(3)
col1.metric("Ticker", company_row["id"])
st.write(company_row["about_company"])

if not sector.empty:
    st.write(f"**Sector:** {sector.iloc[0]['broad_sector']}")
    st.write(f"**Sub Sector:** {sector.iloc[0]['sub_sector']}")

# -------------------------
# FIX: pick latest non-TTM row for ratios that TTM doesn't populate
# -------------------------
ratios_sorted = ratios.sort_values("year")
non_ttm = ratios_sorted[ratios_sorted["year"] != "TTM"]
latest = non_ttm.iloc[-1] if not non_ttm.empty else ratios_sorted.iloc[-1]

c1, c2, c3 = st.columns(3)

c1.metric(
    "Net Profit Margin",
    round(latest["net_profit_margin_pct"], 2) if pd.notna(latest["net_profit_margin_pct"]) else "N/A"
)
c2.metric(
    "Debt To Equity",
    round(latest["debt_to_equity"], 2) if pd.notna(latest["debt_to_equity"]) else "N/A"
)
c3.metric(
    "ROE",
    round(latest["return_on_equity_pct"], 2) if pd.notna(latest["return_on_equity_pct"]) else "N/A"
)

st.divider()

# -------------------------
# Dual-Axis ROE / ROCE Chart
# -------------------------
st.subheader("ROE vs ROCE (Dual Axis)")

chart_data = ratios_sorted[ratios_sorted["year"] != "TTM"].copy()

fig_dual = go.Figure()

fig_dual.add_trace(go.Scatter(
    x=chart_data["year"],
    y=chart_data["return_on_equity_pct"],
    name="ROE %",
    yaxis="y1",
    mode="lines+markers"
))

fig_dual.add_trace(go.Scatter(
    x=chart_data["year"],
    y=chart_data["return_on_capital_employed_pct"],
    name="ROCE %",
    yaxis="y2",
    mode="lines+markers"
))

fig_dual.update_layout(
    yaxis=dict(title="ROE %"),
    yaxis2=dict(title="ROCE %", overlaying="y", side="right"),
    legend=dict(orientation="h", y=1.1)
)

st.plotly_chart(fig_dual, use_container_width=True)

# -------------------------
# Revenue & PAT 10-Year Bar Chart
# -------------------------
st.subheader("Revenue & PAT Trend")

pl = get_pl(ticker)

if pl.empty:
    st.warning("No P&L data available for this company.")
else:
    pl_sorted = pl.sort_values("year")
    pl_sorted = pl_sorted[pl_sorted["year"] != "TTM"]

    fig_pl = px.bar(
        pl_sorted,
        x="year",
        y=["sales", "net_profit"],
        barmode="group",
        title=f"{company_row['company_name']} - Sales vs Net Profit",
        labels={"value": "₹ Crore", "variable": "Metric"}
    )
    st.plotly_chart(fig_pl, use_container_width=True)
st.divider()

# -------------------------
# Pros & Cons
# -------------------------
st.subheader("Pros & Cons")

from utils.db import get_prosandcons  # add this import at top of file too

pc = get_prosandcons(ticker)

if pc.empty:
    st.caption("No pros/cons data available for this company.")
else:
    col_pros, col_cons = st.columns(2)

    with col_pros:
        st.markdown("**Pros**")
        for text in pc["pros"].dropna():
            if str(text).strip():
                st.markdown(f"✅ {text}")

    with col_cons:
        st.markdown("**Cons**")
        for text in pc["cons"].dropna():
            if str(text).strip():
                st.markdown(f"❌ {text}")

st.caption(f"⏱️ Page loaded in {time.time() - _start_time:.2f} seconds")