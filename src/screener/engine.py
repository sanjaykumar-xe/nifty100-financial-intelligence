import sqlite3
from pathlib import Path

import pandas as pd
import yaml

DB = Path("db/nifty100.db")
CONFIG = Path("config/screener_config.yaml")


def load_config():
    with open(CONFIG, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_latest_financial_data():
    conn = sqlite3.connect(DB)

    query = """
    SELECT
        r.*,
        c.company_name,
        s.broad_sector,
        p.sales,
        p.net_profit,
        m.pe_ratio,
        m.pb_ratio,
        m.dividend_yield_pct,
        m.market_cap_crore
    FROM financial_ratios r
    LEFT JOIN companies c 
        ON r.company_id = c.id
    LEFT JOIN sectors s 
        ON r.company_id = s.company_id
    LEFT JOIN profitandloss p 
        ON r.company_id = p.company_id 
        AND r.year = p.year
    LEFT JOIN market_cap m 
        ON r.company_id = m.company_id
        AND m.year = (
            SELECT MAX(year)
            FROM market_cap mc
            WHERE mc.company_id = r.company_id
        )
    WHERE r.year = (
    SELECT MAX(year)
    FROM financial_ratios fr
    WHERE fr.company_id = r.company_id
    AND fr.year != 'TTM'
)
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    df = df.drop_duplicates(subset=["company_id"])

    return df


def to_numeric(df, columns):
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def apply_filters(df, filters):
    df = df.copy()

    numeric_cols = [
        "return_on_equity_pct",
        "debt_to_equity",
        "free_cash_flow_cr",
        "revenue_cagr_5yr",
        "revenue_cagr_3yr",
        "pat_cagr_5yr",
        "operating_profit_margin_pct",
        "pe_ratio",
        "pb_ratio",
        "dividend_yield_pct",
        "dividend_payout_ratio_pct",
        "interest_coverage",
        "market_cap_crore",
        "net_profit",
        "eps_cagr_5yr",
        "asset_turnover",
        "sales",
        "composite_quality_score",
    ]

    df = to_numeric(df, numeric_cols)

    if "roe_min" in filters:
        df = df[df["return_on_equity_pct"] >= filters["roe_min"]]

    if "debt_to_equity_max" in filters:
        max_de = filters["debt_to_equity_max"]
        df = df[
            (df["broad_sector"] == "Financials")
            | (df["debt_to_equity"] <= max_de)
        ]

    if "debt_to_equity_equal" in filters:
        df = df[df["debt_to_equity"] == filters["debt_to_equity_equal"]]

    if "free_cash_flow_min" in filters:
        df = df[df["free_cash_flow_cr"] >= filters["free_cash_flow_min"]]

    if "revenue_cagr_5yr_min" in filters:
        df = df[df["revenue_cagr_5yr"] >= filters["revenue_cagr_5yr_min"]]

    if "revenue_cagr_3yr_min" in filters:
        df = df[df["revenue_cagr_3yr"] >= filters["revenue_cagr_3yr_min"]]

    if "pat_cagr_5yr_min" in filters:
        df = df[df["pat_cagr_5yr"] >= filters["pat_cagr_5yr_min"]]

    if "opm_min" in filters:
        df = df[df["operating_profit_margin_pct"] >= filters["opm_min"]]

    if "pe_max" in filters:
        df = df[df["pe_ratio"] <= filters["pe_max"]]

    if "pb_max" in filters:
        df = df[df["pb_ratio"] <= filters["pb_max"]]

    if "dividend_yield_min" in filters:
        df = df[df["dividend_yield_pct"] >= filters["dividend_yield_min"]]

    if "dividend_payout_max" in filters:
        df = df[df["dividend_payout_ratio_pct"] <= filters["dividend_payout_max"]]

    if "icr_min" in filters:
        min_icr = filters["icr_min"]
        df["icr_effective"] = df["interest_coverage"]
        df.loc[df["icr_label"] == "Debt Free", "icr_effective"] = float("inf")
        df = df[df["icr_effective"] >= min_icr]

    if "market_cap_min" in filters:
        df = df[df["market_cap_crore"] >= filters["market_cap_min"]]

    if "net_profit_min" in filters:
        df = df[df["net_profit"] >= filters["net_profit_min"]]

    if "eps_cagr_min" in filters:
        df = df[df["eps_cagr_5yr"] >= filters["eps_cagr_min"]]

    if "asset_turnover_min" in filters:
        df = df[df["asset_turnover"] >= filters["asset_turnover_min"]]

    if "sales_min" in filters:
        df = df[df["sales"] >= filters["sales_min"]]

    return df.sort_values("composite_quality_score", ascending=False)


if __name__ == "__main__":
    config = load_config()
    df = load_latest_financial_data()

    for preset_name, filters in config["presets"].items():
        result = apply_filters(df, filters)

        print("\n" + "=" * 60)
        print(preset_name.upper())
        print("Result count:", len(result))

        display_cols = [
            "company_id",
            "company_name",
            "return_on_equity_pct",
            "debt_to_equity",
            "free_cash_flow_cr",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "pe_ratio",
            "pb_ratio",
            "dividend_yield_pct",
            "composite_quality_score",
        ]

        existing_cols = [col for col in display_cols if col in result.columns]
        print(result[existing_cols].head(10))