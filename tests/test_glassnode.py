import pytest
import pandas as pd
from unittest.mock import patch, Mock
from chaindl.scraper import glassnode


def test_parse_metric_path_basic():
    url = "https://studio.glassnode.com/charts/addresses.ActiveCountWithContracts?a=ETH"
    path, asset, snake_case = glassnode._parse_metric_path(url)
    assert asset == "ETH"
    assert "active_count_with_contracts" in snake_case
    assert path.endswith(snake_case)


def test_parse_metric_path_default_asset():
    url = "https://studio.glassnode.com/charts/addresses.ActiveCountWithContracts"
    path, asset, snake_case = glassnode._parse_metric_path(url)
    assert asset == "BTC"


def test_process_metric_json_simple():
    json_data = [{"t": 1680000000, "v": 42}, {"t": 1680000600, "v": 43}]
    df = glassnode._process_metric_json(json_data, "metric_name")
    assert isinstance(df, pd.DataFrame)
    assert "metric_name" in df.columns
    assert df.index.name == "Date"


def test_process_metric_json_nested():
    json_data = [
        {"t": 1680000000, "o": {"a": 1, "b": 2}},
        {"t": 1680000600, "o": {"a": 3, "b": 4}},
    ]
    df = glassnode._process_metric_json(json_data, "ignored")
    assert isinstance(df, pd.DataFrame)
    assert "a" in df.columns and "b" in df.columns
    assert df.shape == (2, 2)  # Only a and b remain


@patch("chaindl.scraper.glassnode.SESSION.get")
def test_fetch_json_success(mock_get):
    mock_resp = Mock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {"key": "value"}
    mock_get.return_value = mock_resp
    data = glassnode._fetch_json("https://fakeurl.com")
    assert data["key"] == "value"


@patch("chaindl.scraper.glassnode.SESSION.get")
def test_download_includes_price(mock_get):
    # Mock metric response
    metric_resp = Mock()
    metric_resp.raise_for_status.return_value = None
    metric_resp.json.return_value = [{"t": 1680000000, "v": 100}]
    # Mock price response
    price_resp = Mock()
    price_resp.raise_for_status.return_value = None
    price_resp.json.return_value = [{"t": 1680000000, "v": 50000}]

    mock_get.side_effect = [Mock(), metric_resp, price_resp]  # First GET for cookies
    url = "https://studio.glassnode.com/charts/addresses.ActiveCountWithContracts?a=ETH"

    df = glassnode._download(url)
    assert "price_usd_close" in df.columns
    assert "active_count_with_contracts" in df.columns
    assert isinstance(df, pd.DataFrame)


@patch("chaindl.scraper.glassnode.SESSION.get")
def test_download_raises_on_required_plan(mock_get):
    resp = Mock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = {"requiredPlan": True}
    mock_get.side_effect = [Mock(), resp]

    url = "https://studio.glassnode.com/charts/addresses.ActiveCountWithContracts?a=ETH"
    with pytest.raises(RuntimeError, match="Data error"):
        glassnode._download(url)


# Integration tests
def test_download_active_count_btc():
    url = "https://studio.glassnode.com/charts/addresses.ActiveCount?a=BTC"
    df = glassnode._download(url)
    assert "active_count" in df.columns
    assert "price_usd_close" in df.columns
    assert not df.empty


def test_download_stock_to_flow_btc():
    url = "https://studio.glassnode.com/charts/indicators.StockToFlowRatio?a=BTC"
    df = glassnode._download(url)
    assert "daysTillHalving" in df.columns
    assert "price" in df.columns
    assert "ratio" in df.columns
    assert "price_usd_close" in df.columns
    assert not df.empty


def test_download_invalid_url():
    url = "https://studio.glassnode.com/charts/addresses.NotARealMetric?a=BTC"
    with pytest.raises(RuntimeError):
        glassnode._download(url)
