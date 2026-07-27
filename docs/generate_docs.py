from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os

os.makedirs("docs", exist_ok=True)

styles = getSampleStyleSheet()


def create_pdf(filename, title, lines):
    doc = SimpleDocTemplate(filename)
    story = [Paragraph(f"<b>{title}</b>", styles["Title"])]

    for line in lines:
        story.append(Paragraph(line, styles["BodyText"]))

    doc.build(story)


create_pdf(
    "docs/analyst_guide.pdf",
    "Analyst Guide",
    [
        "Nifty100 Financial Intelligence Platform",
        "1. Open Streamlit dashboard.",
        "2. Use screener filters.",
        "3. Review company rankings.",
        "4. Compare peer companies.",
        "5. Analyze valuation.",
        "6. View cashflow intelligence.",
        "7. Review portfolio recommendations.",
        "8. Export reports.",
    ],
)

create_pdf(
    "docs/acceptance_checklist.pdf",
    "Acceptance Checklist",
    [
        "Database created",
        "Financial ratios calculated",
        "Screeners working",
        "Peer comparison working",
        "Dashboard operational",
        "FastAPI operational",
        "Reports generated",
        "Portfolio engine working",
        "Risk analysis complete",
        "Strategy backtest complete",
        "Recommendation engine complete",
        "Unit tests passing",
    ],
)

print("PDFs generated successfully.")