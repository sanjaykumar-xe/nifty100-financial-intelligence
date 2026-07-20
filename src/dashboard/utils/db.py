import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "db/nifty100.db"


@st.cache_data(ttl=600)
def get_companies():
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(
        """
        SELECT *
        FROM companies
        """,
        conn
    )

    conn.close()
    return df

@st.cache_data(ttl=600)
def get_prosandcons(ticker):
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(
        f"""
        SELECT *
        FROM prosandcons
        WHERE company_id='{ticker}'
        """,
        conn
    )

    conn.close()
    return df


@st.cache_data(ttl=600)
def get_ratios(ticker=None, year=None):

    conn = sqlite3.connect(DB_PATH)

    query = "SELECT * FROM financial_ratios WHERE 1=1"

    if ticker:
        query += f" AND company_id='{ticker}'"

    if year:
        query += f" AND year='{year}'"

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_pl(ticker):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(
        f"""
        SELECT *
        FROM profitandloss
        WHERE company_id='{ticker}'
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_bs(ticker):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(
        f"""
        SELECT *
        FROM balancesheet
        WHERE company_id='{ticker}'
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_cf(ticker):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(
        f"""
        SELECT *
        FROM cashflow
        WHERE company_id='{ticker}'
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_sectors():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(
        """
        SELECT *
        FROM sectors
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_peers(group_name=None):

    conn = sqlite3.connect(DB_PATH)

    query = "SELECT * FROM peer_groups"

    if group_name:
        query += f" WHERE peer_group_name='{group_name}'"

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_valuation(ticker=None):

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        company_id,
        year,
        return_on_equity_pct,
        debt_to_equity,
        return_on_capital_employed_pct,
        composite_quality_score
    FROM financial_ratios
    """

    if ticker:
        query += f" WHERE company_id='{ticker}'"

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df

@st.cache_data(ttl=600)
def get_company_profile(ticker):

    conn = sqlite3.connect(DB_PATH)

    company = pd.read_sql_query(
        f"""
        SELECT *
        FROM companies
        WHERE id='{ticker}'
        """,
        conn
    )

    sector = pd.read_sql_query(
        f"""
        SELECT *
        FROM sectors
        WHERE company_id='{ticker}'
        """,
        conn
    )

    ratios = pd.read_sql_query(
        f"""
        SELECT *
        FROM financial_ratios
        WHERE company_id='{ticker}'
        ORDER BY year
        """,
        conn
    )

    conn.close()

    return company, sector, ratios