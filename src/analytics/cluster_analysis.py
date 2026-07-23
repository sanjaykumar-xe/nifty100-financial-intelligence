import os
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

from scipy.stats import zscore


def run_cluster_analysis():

    os.makedirs("output", exist_ok=True)
    os.makedirs("reports", exist_ok=True)


    # Load data

    ratios = pd.read_csv(
        "data/processed/financial_ratios.csv"
    )

    sectors = pd.read_csv(
        "data/processed/sectors.csv"
    )

    clusters = pd.read_csv(
        "output/cluster_labels.csv"
    )


    # Latest year data

    latest = (
        ratios.sort_values("year")
        .groupby("company_id")
        .tail(1)
    )


    df = latest.merge(
        sectors[
            [
                "company_id",
                "broad_sector"
            ]
        ],
        on="company_id",
        how="left"
    )


    df = df.merge(
        clusters,
        on="company_id",
        how="left"
    )


    # ------------------------------------------------
    # Cluster profiling
    # ------------------------------------------------

    features = [
        "return_on_equity_pct",
        "debt_to_equity",
        "operating_profit_margin_pct",
        "net_profit_margin_pct",
        "interest_coverage"
    ]


    cluster_profile = (
        df.groupby("cluster_name")[features]
        .agg(
            [
                "mean",
                "median"
            ]
        )
    )


    cluster_profile.to_csv(
        "output/cluster_profile.csv"
    )


    print("Cluster profile generated")


    # ------------------------------------------------
    # Correlation heatmap
    # ------------------------------------------------


    kpis = [
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "return_on_equity_pct",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "free_cash_flow_cr",
        "capex_cr",
        "earnings_per_share",
        "book_value_per_share"
    ]


    corr = df[kpis].corr()


    plt.figure(
        figsize=(12,9)
    )

    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f"
    )


    plt.title(
        "Financial KPI Correlation Matrix"
    )


    plt.savefig(
        "reports/correlation_heatmap.png",
        bbox_inches="tight"
    )


    plt.close()


    print("Correlation heatmap generated")


    # ------------------------------------------------
    # Outlier Detection
    # ------------------------------------------------


    outliers = []


    z_features = [
        "return_on_equity_pct",
        "debt_to_equity",
        "operating_profit_margin_pct",
        "net_profit_margin_pct",
        "free_cash_flow_cr"
    ]


    for sector, group in df.groupby(
        "broad_sector"
    ):

        scores = group[z_features].apply(
            zscore
        )


        for index,row in scores.iterrows():

            for col,value in row.items():

                if abs(value) > 3:

                    outliers.append(
                        [
                            df.loc[index,"company_id"],
                            sector,
                            col,
                            value
                        ]
                    )


    outlier_df = pd.DataFrame(
        outliers,
        columns=[
            "company_id",
            "sector",
            "metric",
            "z_score"
        ]
    )


    outlier_df.to_csv(
        "output/outlier_report.csv",
        index=False
    )


    print("Outlier report generated")


    # ------------------------------------------------
    # Portfolio statistics
    # ------------------------------------------------


    stats = df[kpis].describe(
        percentiles=[
            .10,
            .25,
            .50,
            .75,
            .90
        ]
    ).T


    stats = stats[
        [
            "10%",
            "25%",
            "50%",
            "75%",
            "90%",
            "mean",
            "std"
        ]
    ]


    stats.to_csv(
        "output/portfolio_stats.csv"
    )


    print("Portfolio statistics generated")


    print("\nCompleted Day 37 Analysis")


if __name__ == "__main__":

    run_cluster_analysis()