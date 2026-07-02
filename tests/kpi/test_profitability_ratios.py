from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    opm_mismatch_flag,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
)


def test_net_profit_margin_normal():
    assert net_profit_margin(20, 100) == 20


def test_net_profit_margin_zero_sales():
    assert net_profit_margin(20, 0) is None


def test_operating_profit_margin_normal():
    assert operating_profit_margin(30, 100) == 30


def test_opm_mismatch_true():
    assert opm_mismatch_flag(25, 20) is True


def test_opm_mismatch_false():
    assert opm_mismatch_flag(20.5, 20) is False


def test_roe_normal():
    assert return_on_equity(50, 100, 150) == 20


def test_roe_negative_equity():
    assert return_on_equity(50, -200, 100) is None


def test_roa_zero_assets():
    assert return_on_assets(50, 0) is None