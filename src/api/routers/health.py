from fastapi import APIRouter
from datetime import datetime
from src.api.database import get_connection


router = APIRouter()


START_TIME = datetime.now()


@router.get("/health")
def health_check():
    """
    API health status.
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
        "documents",
        "market_cap",
        "analysis"
    ]

    counts = {}

    for table in tables:
        try:
            cursor.execute(
                f"SELECT COUNT(*) FROM {table}"
            )
            counts[table] = cursor.fetchone()[0]

        except Exception:
            counts[table] = 0


    uptime = (
        datetime.now() - START_TIME
    ).total_seconds()


    return {
        "status": "ok",
        "db_row_counts": counts,
        "uptime_seconds": uptime,
        "version": "1.0.0"
    }