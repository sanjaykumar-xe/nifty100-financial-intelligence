import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(layout="wide")
st.title("🔍 Stock Screener")

# Load Data
conn = sqlite3.connect("db/nifty100.db")

ratios = pd.read_sql("SELECT * FROM financial_ratios", conn)
companies = pd.read_sql("SELECT id, company_name FROM companies", conn)
sectors = pd.read_sql("SELECT company_id, broad_sector FROM sectors", conn)
market = pd.read_sql(
    "SELECT company_id, year, pe_ratio, pb_ratio, dividend_yield_pct FROM market_cap WHERE year='2024'",
    conn
)

conn.close()

# Latest ratios record per company (exclude TTM)
ratios = ratios[ratios["year"] != "TTM"]
ratios = ratios.sort_values("year").groupby("company_id").tail(1)

df = ratios.merge(companies, left_on="company_id", right_on="id", how="left")
df = df.merge(sectors, on="company_id", how="left")
df = df.merge(market[["company_id", "pe_ratio", "pb_ratio", "dividend_yield_pct"]], on="company_id", how="left")

numeric_cols = [
    "return_on_equity_pct", "debt_to_equity", "free_cash_flow_cr",
    "revenue_cagr_5yr", "pat_cagr_5yr", "operating_profit_margin_pct",
    "interest_coverage", "pe_ratio", "pb_ratio", "dividend_yield_pct"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

st.sidebar.header("Filters")
st.sidebar.subheader("Presets")
preset = st.sidebar.radio(
    "Quick Filter",
    ["Custom", "Quality", "Value", "Growth", "Dividend", "Debt-Free", "Turnaround"],
    horizontal=False
)

presets = {
    "Quality":    dict(roe=20.0, de=1.0,  fcf=0.0,   revg=10.0, patg=10.0, opm=15.0, pe=60.0,  pb=15.0, div=0.0, icr=3.0),
    "Value":      dict(roe=0.0,  de=2.0,  fcf=0.0,   revg=-50.0, patg=-50.0, opm=0.0, pe=20.0,  pb=3.0,  div=0.0, icr=1.0),
    "Growth":     dict(roe=0.0,  de=10.0, fcf=-5000.0, revg=20.0, patg=20.0, opm=0.0, pe=200.0, pb=50.0, div=0.0, icr=1.0),
    "Dividend":   dict(roe=0.0,  de=10.0, fcf=-5000.0, revg=-50.0, patg=-50.0, opm=0.0, pe=200.0, pb=50.0, div=2.0, icr=1.0),
    "Debt-Free":  dict(roe=0.0,  de=0.05, fcf=-5000.0, revg=-50.0, patg=-50.0, opm=0.0, pe=200.0, pb=50.0, div=0.0, icr=1.0),
    "Turnaround": dict(roe=-50.0, de=10.0, fcf=-5000.0, revg=0.0, patg=0.0, opm=0.0, pe=200.0, pb=50.0, div=0.0, icr=0.0),
}

p = presets.get(preset, None)
roe_min = st.sidebar.slider("Minimum ROE %", 0.0, 100.0, p["roe"] if p else 10.0)
de_max = st.sidebar.slider("Maximum Debt/Equity", 0.0, 10.0, p["de"] if p else 2.0)
fcf_min = st.sidebar.slider("Minimum FCF", -5000.0, 50000.0, p["fcf"] if p else 0.0)
rev_cagr_min = st.sidebar.slider("Revenue CAGR 5Y", -50.0, 100.0, p["revg"] if p else 5.0)
pat_cagr_min = st.sidebar.slider("PAT CAGR 5Y", -50.0, 100.0, p["patg"] if p else 5.0)
opm_min = st.sidebar.slider("Operating Margin %", 0.0, 100.0, p["opm"] if p else 10.0)
pe_max = st.sidebar.slider("Maximum P/E", 0.0, 200.0, p["pe"] if p else 50.0)
pb_max = st.sidebar.slider("Maximum P/B", 0.0, 50.0, p["pb"] if p else 10.0)
dividend_min = st.sidebar.slider("Dividend Yield %", 0.0, 15.0, p["div"] if p else 0.0)
icr_min = st.sidebar.slider("Interest Coverage", 0.0, 500.0, p["icr"] if p else 1.0)

filtered = df[
    (df["return_on_equity_pct"] >= roe_min) &
    (df["debt_to_equity"] <= de_max) &
    (df["free_cash_flow_cr"] >= fcf_min) &
    (df["revenue_cagr_5yr"] >= rev_cagr_min) &
    (df["pat_cagr_5yr"] >= pat_cagr_min) &
    (df["operating_profit_margin_pct"] >= opm_min) &
    (df["pe_ratio"] <= pe_max) &
    (df["pb_ratio"] <= pb_max) &
    (df["dividend_yield_pct"] >= dividend_min) &
    (df["interest_coverage"] >= icr_min)
]

st.subheader(f"{len(filtered)} companies match your filters")

display_cols = [
    "company_id", "company_name", "broad_sector",
    "return_on_equity_pct", "debt_to_equity", "free_cash_flow_cr",
    "revenue_cagr_5yr", "pat_cagr_5yr", "operating_profit_margin_pct",
    "pe_ratio", "pb_ratio", "dividend_yield_pct", "interest_coverage",
    "composite_quality_score"
]
display_cols = [c for c in display_cols if c in filtered.columns]

filtered_display = filtered.copy()
filtered_display[numeric_cols] = filtered_display[numeric_cols].fillna(0)

st.dataframe(filtered_display[display_cols], use_container_width=True)

csv = filtered_display[display_cols].to_csv(index=False)
st.download_button("Download CSV", csv, "screener_results.csv", "text/csv")