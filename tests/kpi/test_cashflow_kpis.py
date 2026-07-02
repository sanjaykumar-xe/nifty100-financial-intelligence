from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_quality_score,
    capex_intensity,
    fcf_conversion_rate,
    capital_allocation_pattern,
)


def test_free_cash_flow():
    assert free_cash_flow(500, -200) == 300


def test_cfo_quality_high():
    assert cfo_quality_score(120, 100) == "High Quality"


def test_cfo_quality_moderate():
    assert cfo_quality_score(70, 100) == "Moderate"


def test_cfo_quality_low():
    assert cfo_quality_score(20, 100) == "Accrual Risk"


def test_capex_asset_light():
    _, label = capex_intensity(-20, 1000)
    assert label == "Asset Light"


def test_fcf_conversion():
    assert fcf_conversion_rate(300, 600) == 50


def test_pattern_reinvestor():
    assert capital_allocation_pattern(100, -50, -20) == "Reinvestor"


def test_pattern_growth_debt():
    assert capital_allocation_pattern(-100, -50, 80) == "Growth Funded by Debt"