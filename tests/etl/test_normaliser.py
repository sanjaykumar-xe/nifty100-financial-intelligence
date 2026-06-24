import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.etl.normaliser import normalize_year, normalize_ticker


@pytest.mark.parametrize("input_value,expected", [
    ("2024", 2024),
    ("FY2024", 2024),
    ("Mar-24", 2024),
    ("Mar 2024", 2024),
    ("2023.0", 2023),
    (2022, 2022),
    (2021.0, 2021),
    ("Year 2020", 2020),
    ("2019", 2019),
    ("FY 2018", 2018),
    ("Mar-17", 2017),
    ("Dec-16", 2016),
    ("2015-03", 2015),
    ("2014/15", 2014),
    ("No year", None),
    ("", None),
    (None, None),
    ("abc", None),
    ("FY2030", 2030),
    ("Mar-10", 2010),
])
def test_normalize_year(input_value, expected):
    assert normalize_year(input_value) == expected


@pytest.mark.parametrize("input_value,expected", [
    ("tcs", "TCS"),
    (" TCS ", "TCS"),
    ("tcs.ns", "TCS"),
    ("INFY", "INFY"),
    (" hdfcbank ", "HDFCBANK"),
    ("bajaj-auto", "BAJAJ-AUTO"),
    ("ultracemco\n", "ULTRACEMCO"),
    ("wipro\r", "WIPRO"),
    ("zomato ", "ZOMATO"),
    ("axis bank", "AXISBANK"),
    ("reliance.ns", "RELIANCE"),
    ("sbin", "SBIN"),
    ("", ""),
    (None, None),
    ("  vedl  ", "VEDL"),
])
def test_normalize_ticker(input_value, expected):
    assert normalize_ticker(input_value) == expected