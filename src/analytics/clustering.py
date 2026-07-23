import os
import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances

import matplotlib.pyplot as plt


def calculate_cagr(start, end, years):
    """
    Calculate CAGR percentage.
    """

    try:
        if start <= 0 or end <= 0:
            return np.nan

        return ((end / start) ** (1 / years) - 1) * 100

    except Exception:
        return np.nan


def generate_clustering():

    os.makedirs("output", exist_ok=True)
    os.makedirs("reports", exist_ok=True)


    # Load datasets

    ratios = pd.read_csv(
        "data/processed/financial_ratios.csv"
    )

    pnl = pd.read_csv(
        "data/processed/profitandloss.csv"
    )

    cashflow = pd.read_csv(
        "data/processed/cashflow.csv"
    )

    sectors = pd.read_csv(
        "data/processed/sectors.csv"
    )


    # Latest financial year per company

    latest = (
        ratios.sort_values("year")
        .groupby("company_id")
        .tail(1)
    )


    # ----------------------------
    # Revenue CAGR calculation
    # ----------------------------

    revenue_data = []

    for company, data in pnl.groupby("company_id"):

        data = data.sort_values("year")

        if len(data) >= 5:

            start = data.iloc[-5]["sales"]
            end = data.iloc[-1]["sales"]

            revenue_data.append(
                [
                    company,
                    calculate_cagr(
                        start,
                        end,
                        5
                    )
                ]
            )


    revenue_cagr = pd.DataFrame(
        revenue_data,
        columns=[
            "company_id",
            "revenue_cagr_5yr"
        ]
    )


    # ----------------------------
    # FCF CAGR calculation
    # ----------------------------

    fcf_data = []

    for company, data in cashflow.groupby("company_id"):

        data = data.sort_values("year")

        if len(data) >= 5:

            start = data.iloc[-5]["net_cash_flow"]
            end = data.iloc[-1]["net_cash_flow"]

            fcf_data.append(
                [
                    company,
                    calculate_cagr(
                        start,
                        end,
                        5
                    )
                ]
            )


    fcf_cagr = pd.DataFrame(
        fcf_data,
        columns=[
            "company_id",
            "fcf_cagr_5yr"
        ]
    )


    # ----------------------------
    # Merge datasets
    # ----------------------------

    df = latest.merge(
        revenue_cagr,
        on="company_id",
        how="left"
    )


    df = df.merge(
        fcf_cagr,
        on="company_id",
        how="left"
    )


    df = df.merge(
        sectors[
            [
                "company_id",
                "broad_sector"
            ]
        ],
        on="company_id",
        how="left"
    )


    features = [
        "return_on_equity_pct",
        "debt_to_equity",
        "revenue_cagr_5yr",
        "fcf_cagr_5yr",
        "operating_profit_margin_pct"
    ]


    # ----------------------------
    # Missing value handling
    # ----------------------------

    for col in features:

        # sector median

        df[col] = (
            df.groupby("broad_sector")[col]
            .transform(
                lambda x: x.fillna(x.median())
            )
        )


        # global median fallback

        df[col] = df[col].fillna(
            df[col].median()
        )


    # Final safety check

    df[features] = df[features].replace(
        [np.inf, -np.inf],
        np.nan
    )


    df[features] = df[features].fillna(
        0
    )


    X = df[features]


    # ----------------------------
    # Scaling
    # ----------------------------

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(
        X
    )


    # ----------------------------
    # Elbow curve
    # ----------------------------

    inertia = []


    for k in range(2,11):

        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10
        )

        model.fit(
            X_scaled
        )

        inertia.append(
            model.inertia_
        )


    plt.figure(
        figsize=(8,5)
    )

    plt.plot(
        range(2,11),
        inertia,
        marker="o"
    )


    plt.xlabel(
        "Number of Clusters"
    )

    plt.ylabel(
        "Inertia"
    )

    plt.title(
        "KMeans Elbow Curve"
    )


    plt.savefig(
        "reports/elbow_plot.png",
        bbox_inches="tight"
    )


    plt.close()



    # ----------------------------
    # Final KMeans
    # ----------------------------

    kmeans = KMeans(
        n_clusters=5,
        random_state=42,
        n_init=10
    )


    clusters = kmeans.fit_predict(
        X_scaled
    )


    distances = pairwise_distances(
        X_scaled,
        kmeans.cluster_centers_
    )


    df["cluster_id"] = clusters


    df["distance_from_centroid"] = (
        distances.min(axis=1)
    )


    cluster_names = {

        0: "High Quality Compounders",

        1: "Defensive Dividend Payers",

        2: "Value Cyclicals",

        3: "Turnaround Candidates",

        4: "Emerging Growth"
    }


    df["cluster_name"] = (
        df["cluster_id"]
        .map(cluster_names)
    )


    output = df[
        [
            "company_id",
            "cluster_id",
            "cluster_name",
            "distance_from_centroid"
        ]
    ]


    output.to_csv(
        "output/cluster_labels.csv",
        index=False
    )


    print(
        "✅ KMeans clustering completed"
    )

    print(
        output.head()
    )

    print(
        "\nCluster distribution:"
    )

    print(
        output["cluster_name"].value_counts()
    )



if __name__ == "__main__":

    generate_clustering()