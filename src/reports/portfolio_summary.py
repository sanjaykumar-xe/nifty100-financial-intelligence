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


def generate_portfolio_summary(output_pdf):

    companies = pd.read_csv(
        "data/processed/companies.csv"
    )

    ratios = pd.read_csv(
        "data/processed/financial_ratios.csv"
    )

    sectors = pd.read_csv(
        "data/processed/sectors.csv"
    )


    df = companies.merge(
        ratios,
        left_on="id",
        right_on="company_id",
        how="inner"
    )


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


    elements=[]


    elements.append(
        Paragraph(
            "Nifty 100 Portfolio Intelligence Summary",
            styles["Title"]
        )
    )


    elements.append(
        Spacer(1,20)
    )


    # Overall metrics

    summary = [
        [
            "Metric",
            "Value"
        ],
        [
            "Total Companies",
            str(df["company_id"].nunique())
        ],
        [
            "Average ROE",
            str(round(df["roe_percentage"].mean(),2))
        ],
        [
            "Average ROCE",
            str(round(df["roce_percentage"].mean(),2))
        ],
        [
            "Average Profit Margin",
            str(round(df["net_profit_margin_pct"].mean(),2))
        ]
    ]


    table = Table(summary)


    table.setStyle(
        TableStyle([
            ("GRID",(0,0),(-1,-1),0.5,None)
        ])
    )


    elements.append(table)


    elements.append(
        Spacer(1,25)
    )


    # Top companies by ROE

    elements.append(
        Paragraph(
            "Top Companies by ROE",
            styles["Heading2"]
        )
    )


    top = (
        df.sort_values(
            "roe_percentage",
            ascending=False
        )
        .drop_duplicates(
            "company_id"
        )
        .head(10)
    )


    top_data=[
        [
            "Company",
            "ROE"
        ]
    ]


    for _,row in top.iterrows():

        top_data.append(
            [
                row["company_name"],
                round(row["roe_percentage"],2)
            ]
        )


    table=Table(top_data)


    table.setStyle(
        TableStyle([
            ("GRID",(0,0),(-1,-1),0.5,None)
        ])
    )


    elements.append(table)


    doc.build(elements)



if __name__ == "__main__":

    generate_portfolio_summary(
        "reports/portfolio_summary.pdf"
    )

    print(
        "Portfolio summary generated successfully"
    )