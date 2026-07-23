import pandas as pd

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet


def generate_tearsheet(excel_path, output_pdf):

    xls = pd.ExcelFile(excel_path)

    profile = pd.read_excel(xls, "Profile")
    financials = pd.read_excel(xls, "Financials")
    valuation = pd.read_excel(xls, "Valuation")
    pros = pd.read_excel(xls, "Pros")
    cons = pd.read_excel(xls, "Cons")


    styles = getSampleStyleSheet()

    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4
    )

    elements = []


    # Company Profile

    company = profile.loc[
        profile["Field"] == "Company Name",
        "Value"
    ].values[0]


    elements.append(
        Paragraph(
            company,
            styles["Title"]
        )
    )

    elements.append(Spacer(1,20))


    profile_data = []

    for _, row in profile.iterrows():
        profile_data.append(
            [
                str(row["Field"]),
                str(row["Value"])
            ]
        )


    table = Table(profile_data)

    table.setStyle(
        TableStyle([
            ("GRID",(0,0),(-1,-1),0.5,None)
        ])
    )

    elements.append(table)


    elements.append(PageBreak())


    # Financials

    elements.append(
        Paragraph(
            "Financial Snapshot",
            styles["Heading2"]
        )
    )


    financial_data = []

    columns = [
        "net_profit_margin_pct",
        "eps_cagr_10yr",
        "composite_quality_score"
    ]


    for col in columns:
        if col in financials.columns:

            financial_data.append(
                [
                    col,
                    str(financials.iloc[0][col])
                ]
            )


    table = Table(financial_data)

    table.setStyle(
        TableStyle([
            ("GRID",(0,0),(-1,-1),0.5,None)
        ])
    )

    elements.append(table)


    elements.append(Spacer(1,20))


    # Valuation

    elements.append(
        Paragraph(
            "Valuation",
            styles["Heading2"]
        )
    )


    valuation_data=[]

    for col in valuation.columns:

        valuation_data.append(
            [
                col,
                str(valuation.iloc[0][col])
            ]
        )


    table = Table(
        valuation_data
    )

    table.setStyle(
        TableStyle([
            ("GRID",(0,0),(-1,-1),0.5,None)
        ])
    )


    elements.append(table)


    elements.append(PageBreak())


    # Pros

    elements.append(
        Paragraph(
            "Strengths",
            styles["Heading2"]
        )
    )


    for _, row in pros.iterrows():

        elements.append(
            Paragraph(
                f"✓ {row['text']} "
                f"(Confidence: {row['confidence_pct']}%)",
                styles["BodyText"]
            )
        )

        elements.append(
            Spacer(1,10)
        )


    # Cons

    elements.append(
        Paragraph(
            "Risks",
            styles["Heading2"]
        )
    )


    for _, row in cons.iterrows():

        elements.append(
            Paragraph(
                f"⚠ {row['text']} "
                f"(Confidence: {row['confidence_pct']}%)",
                styles["BodyText"]
            )
        )


    doc.build(elements)



if __name__ == "__main__":

    generate_tearsheet(
        "reports/tearsheets/TCS_tearsheet.xlsx",
        "reports/tearsheets/TCS_tearsheet.pdf"
    )

    print("PDF generated successfully")