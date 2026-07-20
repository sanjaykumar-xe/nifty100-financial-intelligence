import streamlit as st
import sqlite3
import pandas as pd

st.title("📑 Annual Reports")

conn = sqlite3.connect("db/nifty100.db")

companies = pd.read_sql(
    """
    SELECT
        id,
        company_name
    FROM companies
    """,
    conn
)

documents = pd.read_sql(
    """
    SELECT *
    FROM documents
    """,
    conn
)

conn.close()

# -------------------------
# Company Selection
# -------------------------

company_ids = sorted(
    companies["id"].unique()
)

selected_company = st.selectbox(
    "Select Company",
    company_ids
)

company_name = companies.loc[
    companies["id"] == selected_company,
    "company_name"
].values[0]

st.subheader(company_name)

# -------------------------
# Reports
# -------------------------

company_docs = documents[
    documents["company_id"] == selected_company
]

if company_docs.empty:
    st.warning("No reports available for this company.")
else:
    st.success(f"{len(company_docs)} reports found")

    display_cols = [c for c in ["Year", "Annual_Report"] if c in company_docs.columns]

    st.dataframe(
        company_docs[display_cols].sort_values("Year", ascending=False),
        use_container_width=True
    )

    st.subheader("Report Links")

    for _, row in company_docs.sort_values("Year", ascending=False).iterrows():
        year_text = str(row["Year"]) if pd.notna(row["Year"]) else "Unknown Year"
        url = row["Annual_Report"]

        if pd.isna(url) or str(url).strip().lower() == "null":
            st.markdown(f"📄 {year_text} — 🔴 Report unavailable")
        else:
            st.markdown(f"📄 [{year_text}]({url})")
# -------------------------
# Raw Data
# -------------------------

with st.expander("View Raw Data"):
    st.dataframe(
        company_docs,
        use_container_width=True
    )