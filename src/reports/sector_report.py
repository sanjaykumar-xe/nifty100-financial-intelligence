import pandas as pd

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet


def generate_sector_report(output_pdf):

    # Load datasets
    companies = pd.read_csv(
        "data/processed/companies.csv"
    )

    ratios = pd.read_csv(
        "data/processed/financial_ratios.csv"
    )

    sectors = pd.read_csv(
        "data/processed/sectors.csv"
    )


    # Merge company + financial ratios
    df = companies.merge(
        ratios,
        left_on="id",
        right_on="company_id",
        how="inner"
    )


    # Merge sector information
    df = df.merge(
        sectors,
        on="company_id",
        how="inner"
    )


    styles = getSampleStyleSheet()

    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4
    )


    elements = []


    elements.append(
        Paragraph(
            "Nifty 100 Sector Intelligence Report",
            styles["Title"]
        )
    )

    elements.append(
        Spacer(1, 20)
    )


    # Sector summary

    sector_summary = (
        df.groupby("broad_sector")
        .agg(
            companies=("company_id", "count"),
            avg_roe=("roe_percentage", "mean"),
            avg_roce=("roce_percentage", "mean"),
            avg_profit_margin=("net_profit_margin_pct", "mean")
        )
        .reset_index()
    )


    data = [
        [
            "Sector",
            "Companies",
            "Avg ROE",
            "Avg ROCE",
            "Avg Profit Margin"
        ]
    ]


    for _, row in sector_summary.iterrows():

        data.append(
            [
                str(row["broad_sector"]),
                str(row["companies"]),
                round(row["avg_roe"], 2),
                round(row["avg_roce"], 2),
                round(row["avg_profit_margin"], 2)
            ]
        )


    table = Table(
        data,
        repeatRows=1
    )


    table.setStyle(
        TableStyle([
            ("GRID", (0,0), (-1,-1), 0.5, None)
        ])
    )


    elements.append(table)


    doc.build(elements)



if __name__ == "__main__":

    generate_sector_report(
        "reports/sector_report.pdf"
    )

    print(
        "Sector report generated successfully"
    )