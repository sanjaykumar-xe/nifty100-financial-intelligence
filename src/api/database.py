import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "db" / "nifty100.db"


def get_connection():
    """
    Create SQLite database connection.
    """
    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    return conn


def get_table_counts():
    """
    Return row counts for all database tables.
    """
    conn = get_connection()
    cursor = conn.cursor()

    tables = [
        "companies",
        "financial_ratios",
        "profitandloss",
        "balancesheet",
        "cashflow",
        "sectors",
        "peer_groups",
        "peer_percentiles",
        "documents",
        "validation_failures"
    ]

    counts = {}

    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = cursor.fetchone()[0]
        except Exception:
            counts[table] = 0

    conn.close()

    return counts