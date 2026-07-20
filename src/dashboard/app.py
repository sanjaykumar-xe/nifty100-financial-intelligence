import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Mutual Fund Intelligence Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 Mutual Fund Intelligence Dashboard")
st.markdown(
    """
    An AI-powered mutual fund analytics platform for fund screening,
    NAV analysis, AUM trends, investor insights, and portfolio intelligence.
    """
)

# Sidebar
st.sidebar.title("Navigation")

page = st.sidebar.selectbox(
    "Select Module",
    [
        "🏠 Home",
        "🔍 Fund Screener",
        "📈 NAV Analysis",
        "💰 AUM Analysis",
        "📥 SIP Inflow Analysis",
        "👥 Investor Insights",
        "🤖 ML Predictions"
    ]
)


# Home Page
if page == "🏠 Home":

    st.subheader("Dashboard Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Funds",
            value="40"
        )

    with col2:
        st.metric(
            label="Fund Houses",
            value="10+"
        )

    with col3:
        st.metric(
            label="NAV Records",
            value="46,000+"
        )

    with col4:
        st.metric(
            label="Investor Transactions",
            value="32,000+"
        )

    st.divider()

    st.info(
        """
        Use the sidebar to explore different mutual fund intelligence modules.
        """
    )


# Fund Screener
elif page == "🔍 Fund Screener":

    st.header("🔍 Mutual Fund Screener")

    st.write(
        "Filter mutual funds based on performance, risk, category, and returns."
    )

    col1, col2 = st.columns(2)

    with col1:
        category = st.selectbox(
            "Select Category",
            [
                "All",
                "Equity",
                "Debt",
                "Hybrid"
            ]
        )

    with col2:
        risk = st.selectbox(
            "Risk Level",
            [
                "All",
                "Low",
                "Moderate",
                "High"
            ]
        )

    st.warning(
        "Database connection and filtering logic will be added here."
    )


# NAV Analysis
elif page == "📈 NAV Analysis":

    st.header("📈 NAV Trend Analysis")

    st.write(
        "Visualize NAV growth trends of mutual fund schemes."
    )

    st.warning(
        "NAV charts will be connected with nav_history.csv"
    )


# AUM Analysis
elif page == "💰 AUM Analysis":

    st.header("💰 Assets Under Management Analysis")

    st.write(
        "Analyze fund house AUM growth and market share."
    )

    st.warning(
        "AUM visualization will be added here."
    )


# SIP Analysis
elif page == "📥 SIP Inflow Analysis":

    st.header("📥 SIP Inflow Analysis")

    st.write(
        "Track monthly SIP investment trends."
    )

    st.warning(
        "SIP time-series charts will be added here."
    )


# Investor Insights
elif page == "👥 Investor Insights":

    st.header("👥 Investor Analytics")

    st.write(
        "Understand investor transactions and demographics."
    )

    st.warning(
        "Investor segmentation module coming soon."
    )


# ML Predictions
elif page == "🤖 ML Predictions":

    st.header("🤖 AI-Based Predictions")

    st.write(
        """
        Future ML models:
        
        - Fund performance prediction
        - Risk classification
        - Return forecasting
        - Portfolio recommendation
        """
    )

    st.warning(
        "Machine learning pipeline will be integrated here."
    )


# Footer
st.divider()

st.caption(
    "Built for Bluestock Mutual Fund Intelligence Capstone Project"
)