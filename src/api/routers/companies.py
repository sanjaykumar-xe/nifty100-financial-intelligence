from fastapi import APIRouter, HTTPException
from src.api.database import get_connection

router = APIRouter()


@router.get("/companies")
def get_companies(
    sector: str | None = None,
    market_cap_category: str | None = None,
    search: str | None = None
):
    """
    Return company list with optional filters.
    """

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT
        c.id AS company_id,
        c.company_name,
        s.broad_sector,
        s.sub_sector,
        c.roe_percentage AS roe_pct,
        c.roce_percentage AS roce_pct,
        s.market_cap_category
    FROM companies c
    LEFT JOIN sectors s
        ON c.id = s.company_id
    WHERE 1=1
    """

    params = []

    if sector:
        query += " AND s.broad_sector = ?"
        params.append(sector)

    if market_cap_category:
        query += " AND s.market_cap_category = ?"
        params.append(market_cap_category)

    if search:
        query += """
        AND (
            c.company_name LIKE ?
            OR c.id LIKE ?
        )
        """
        params.extend([
            f"%{search}%",
            f"%{search}%"
        ])

    rows = cursor.execute(query, params).fetchall()

    conn.close()

    return [dict(row) for row in rows]


@router.get("/companies/{company_id}")
def company_profile(company_id: str):
    """
    Return complete company profile.
    """

    conn = get_connection()
    cursor = conn.cursor()

    company = cursor.execute(
        """
        SELECT
            c.*,
            s.broad_sector,
            s.sub_sector,
            s.market_cap_category
        FROM companies c
        LEFT JOIN sectors s
            ON c.id = s.company_id
        WHERE c.id = ?
        """,
        (company_id,)
    ).fetchone()

    conn.close()

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    return dict(company)


@router.get("/companies/{company_id}/ratios")
def company_ratios(company_id: str):
    """
    Return financial ratios.
    """

    conn = get_connection()
    cursor = conn.cursor()

    rows = cursor.execute(
        """
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
        ORDER BY year DESC
        """,
        (company_id,)
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


@router.get("/companies/{company_id}/pl")
def company_profit_loss(company_id: str):
    """
    Return Profit & Loss statements.
    """

    conn = get_connection()
    cursor = conn.cursor()

    rows = cursor.execute(
        """
        SELECT *
        FROM profitandloss
        WHERE company_id = ?
        ORDER BY year DESC
        """,
        (company_id,)
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


@router.get("/companies/{company_id}/bs")
def company_balance_sheet(company_id: str):
    """
    Return Balance Sheet.
    """

    conn = get_connection()
    cursor = conn.cursor()

    rows = cursor.execute(
        """
        SELECT *
        FROM balancesheet
        WHERE company_id = ?
        ORDER BY year DESC
        """,
        (company_id,)
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


@router.get("/companies/{company_id}/cashflow")
def company_cashflow(company_id: str):
    """
    Return Cash Flow statement.
    """

    conn = get_connection()
    cursor = conn.cursor()

    rows = cursor.execute(
        """
        SELECT *
        FROM cashflow
        WHERE company_id = ?
        ORDER BY year DESC
        """,
        (company_id,)
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


@router.get("/companies/{company_id}/tearsheet")
def company_tearsheet(company_id: str):
    """
    Return complete company tear sheet.
    """

    conn = get_connection()
    cursor = conn.cursor()

    company = cursor.execute(
        """
        SELECT
            c.*,
            s.broad_sector,
            s.sub_sector,
            s.market_cap_category
        FROM companies c
        LEFT JOIN sectors s
            ON c.id = s.company_id
        WHERE c.id = ?
        """,
        (company_id,)
    ).fetchone()

    if not company:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    ratios = cursor.execute(
        """
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
        ORDER BY year DESC
        LIMIT 5
        """,
        (company_id,)
    ).fetchall()

    profit_loss = cursor.execute(
        """
        SELECT *
        FROM profitandloss
        WHERE company_id = ?
        ORDER BY year DESC
        LIMIT 5
        """,
        (company_id,)
    ).fetchall()

    balance_sheet = cursor.execute(
        """
        SELECT *
        FROM balancesheet
        WHERE company_id = ?
        ORDER BY year DESC
        LIMIT 5
        """,
        (company_id,)
    ).fetchall()

    cash_flow = cursor.execute(
        """
        SELECT *
        FROM cashflow
        WHERE company_id = ?
        ORDER BY year DESC
        LIMIT 5
        """,
        (company_id,)
    ).fetchall()

    conn.close()

    return {
        "company": dict(company),
        "financial_ratios": [dict(row) for row in ratios],
        "profit_loss": [dict(row) for row in profit_loss],
        "balance_sheet": [dict(row) for row in balance_sheet],
        "cash_flow": [dict(row) for row in cash_flow],
    }