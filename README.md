\# NIFTY 100 Financial Intelligence Platform



A full-stack financial analytics platform covering all 92 NIFTY100 companies — built as a Bluestock Fintech Data Analyst internship capstone project.



\## Overview



This project ingests 12 source Excel datasets into a validated SQLite database, computes 50+ financial ratios and KPIs per company per year, and surfaces the results through an 8-screen interactive Streamlit dashboard with a dedicated valuation and screening engine.



\## Tech Stack



\- \*\*Data \& ETL:\*\* Python, Pandas, SQLite

\- \*\*Dashboard:\*\* Streamlit, Plotly

\- \*\*Reporting:\*\* OpenPyXL, ReportLab

\- \*\*Testing:\*\* Pytest



\## Running the Dashboard



```bash

streamlit run src/dashboard/app.py

```



The app opens at `http://localhost:8501` with sidebar navigation to all 8 screens.



\## Rebuilding the Financial Ratios Table



If source data changes, regenerate `financial\_ratios`:



```bash

python -m src.analytics.populate\_financial\_ratios

```



\## Generating the Valuation Module Output



```bash

python -m src.analytics.valuation

```



Produces:

\- `output/valuation\_summary.xlsx` — 92 companies with P/E, P/B, EV/EBITDA, FCF yield, and valuation flags

\- `output/valuation\_flags.csv` — companies flagged Caution or Discount



\## Dashboard Screens



| # | Screen | Description |

|---|--------|-------------|

| 1 | \*\*Home\*\* | 6 summary KPI tiles (Average ROE, Median P/E, Median D/E, Total Companies, Revenue CAGR 5Y, Debt-Free count), sector distribution donut chart, Top 5 Quality Companies table, year selector |

| 2 | \*\*Company Profile\*\* | Company search, sector/sub-sector card, 3 KPI tiles (Net Profit Margin, D/E, ROE), ROE vs ROCE dual-axis trend chart, Revenue vs Net Profit bar chart, Pros \& Cons badges (where source data available) |

| 3 | \*\*Stock Screener\*\* | 10-metric filter engine (ROE, D/E, FCF, Revenue CAGR, PAT CAGR, Operating Margin, P/E, P/B, Dividend Yield, Interest Coverage), 6 quick-filter presets (Quality, Value, Growth, Dividend, Debt-Free, Turnaround), live result count, CSV export |

| 4 | \*\*Peer Comparison\*\* | Peer group selector (11 groups), radar chart comparing a company's 8 metrics against its peer group average, full peer comparison table |

| 5 | \*\*Trend Analysis\*\* | Multi-metric selector (up to 3 overlaid metrics), 10+ year line chart, Year-over-Year % change table |

| 6 | \*\*Sector Analysis\*\* | Sector selector, Revenue vs ROE bubble chart (bubble size = market cap, colour = sub-sector), sector median KPI tiles |

| 7 | \*\*Capital Allocation Map\*\* | Treemap of all 92 companies grouped into capital allocation patterns (Stable, Compounders, Cash Generators, Turnaround, etc.), drill-down table per pattern |

| 8 | \*\*Annual Reports\*\* | Company search, list of available annual report years with clickable BSE filing links, red "Report unavailable" badge for missing/broken links |



\## Data Pipeline Notes



\- \*\*ROE / ROCE calculation:\*\* Computed per-year from balance sheet data (`net\_profit / (equity\_capital + reserves)`), with two safety layers:

&#x20; 1. Values outside a realistic 0–100% range are rejected

&#x20; 2. Values that deviate more than 2.5x from a company's own historical median are treated as outliers (e.g. caused by corporate actions such as bonus/rights issues distorting the equity base in a single year)

&#x20; 

&#x20; In both cases, the pipeline falls back to the company's trusted static ROE/ROCE value (sourced from `companies.roe\_percentage` / `roce\_percentage`) rather than showing an unrealistic or missing figure.



\- \*\*TTM (Trailing Twelve Month) rows:\*\* Excluded from "latest year" selection logic across all screens, since TTM rows do not carry multi-year metrics like CAGR.



\- \*\*Fiscal year-end transitions:\*\* A small number of companies (e.g. Ambuja Cements) have a stretched fiscal period label (e.g. "Mar 2023 15" for a 15-month transition year) where balance sheet data doesn't join cleanly to the profit \& loss data for that period. These rows display as N/A rather than crashing.



\- \*\*Pros \& Cons coverage:\*\* Source data currently includes pros/cons only for a subset of companies (HDFCBANK, SBILIFE, INFY, TCS). Other companies correctly display "No pros/cons data available."



\## Known Limitations



\- Peer Comparison radar chart mixes percentage-based metrics (ROE, D/E) with absolute ₹ Crore metrics (FCF) on a shared radial scale, which can visually compress smaller values.

\- Peer benchmark-row highlighting is not yet implemented.



\## Sprint 4 QA Summary



\- All 8 screens tested across ABB, ADANIGREEN, HINDUNILVR, LT, BEL, AMBUJACEM, and SIEMENS, spanning Industrials, Energy, FMCG, Financials, and Materials sectors — no crashes.

\- Screener tested at both extreme-restrictive (0 matches, graceful empty state) and extreme-permissive (full match set) slider settings — no errors in either case.

\- Company Profile page load time measured at 0.52s for ABB — well under the 3-second requirement.

\- Screener CSV export verified to produce valid output with correct headers.

\- `valuation\_summary.xlsx` verified at 92 rows with all required columns; `valuation\_flags.csv` produced 44 flagged companies.

