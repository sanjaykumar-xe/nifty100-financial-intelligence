from pathlib import Path
import sqlite3
import pandas as pd
import time

PROCESSED = Path("data/processed")
DB_PATH = Path("db/nifty100.db")
SCHEMA_PATH = Path("db/schema.sql")
OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

LOAD_ORDER = [
    "companies",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "analysis",
    "documents",
    "prosandcons",
    "sectors",
    "stock_prices",
    "market_cap",
    "financial_ratios",
]


def load_schema(conn):
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())


def load_table(conn, table):
    start = time.time()

    csv_path = PROCESSED / f"{table}.csv"
    df = pd.read_csv(csv_path)

    rows_in = len(df)

    table_cols = pd.read_sql_query(f"PRAGMA table_info({table});", conn)["name"].tolist()
    df = df[[col for col in df.columns if col in table_cols]]

    df.to_sql(table, conn, if_exists="append", index=False)

    runtime = round(time.time() - start, 2)

    return {
        "table": table,
        "rows_in": rows_in,
        "rows_loaded": rows_in,
        "rejected": 0,
        "runtime_seconds": runtime
    }


def main():
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    load_schema(conn)

    audit = []

    for table in LOAD_ORDER:
        print(f"Loading {table}...")
        audit.append(load_table(conn, table))

    fk_check = pd.read_sql_query("PRAGMA foreign_key_check;", conn)
    fk_check.to_csv(OUTPUT / "foreign_key_check.csv", index=False)

    pd.DataFrame(audit).to_csv(OUTPUT / "load_audit.csv", index=False)

    conn.commit()
    conn.close()

    print("\nSQLite load completed.")
    print("Saved:", DB_PATH)
    print("Saved: output/load_audit.csv")
    print("Saved: output/foreign_key_check.csv")


if __name__ == "__main__":
    main()