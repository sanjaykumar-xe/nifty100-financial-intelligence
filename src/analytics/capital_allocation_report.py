import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path("output")

df = pd.read_csv(
    OUTPUT_DIR / "capital_allocation.csv"
)

# -----------------------------
# Latest Year Distribution
# -----------------------------

latest_rows = (
    df[df["year"] != "TTM"]
      .copy()
)

latest_rows = (
    latest_rows
      .sort_values("year")
      .groupby("company_id")
      .tail(1)
)

distribution = (
    latest_rows["pattern_label"]
    .value_counts()
    .reset_index()
)

distribution.columns = [
    "pattern_label",
    "company_count"
]

distribution.to_csv(
    OUTPUT_DIR / "capital_allocation_distribution.csv",
    index=False
)

# -----------------------------
# Pattern Changes
# -----------------------------

changes = []

for company_id, grp in df[df["year"] != "TTM"].groupby("company_id"):

    grp = grp.sort_values("year")

    if len(grp) < 2:
        continue

    old_pattern = grp.iloc[-2]["pattern_label"]
    new_pattern = grp.iloc[-1]["pattern_label"]

    if old_pattern != new_pattern:

        changes.append({
            "company_id": company_id,
            "previous_pattern": old_pattern,
            "current_pattern": new_pattern
        })

changes_df = pd.DataFrame(changes)

changes_df.to_csv(
    OUTPUT_DIR / "pattern_changes.csv",
    index=False
)

print(
    "Distribution rows:",
    len(distribution)
)

print(
    "Pattern changes:",
    len(changes_df)
)

print(
    "Saved -> output/capital_allocation_distribution.csv"
)

print(
    "Saved -> output/pattern_changes.csv"
)