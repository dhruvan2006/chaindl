import pytest
import pandas as pd
from unittest.mock import Mock

from chaindl.scraper.woocharts import _request_chart_json, _download


@pytest.fixture
def mock_response():
    return {
        "chart1": {"x": [1620000000000, 1620003600000], "y": ["1.1", "1.2"]},
        "chart2": {"x": [1620000000000, 1620003600000], "y": ["2.1", "2.2"]},
    }


def test_request_chart_json(mocker, mock_response):
    url = "https://example.com"
    mocker.patch("requests.get")
    mock_requests = mocker.patch(
        "requests.get", return_value=Mock(json=lambda: mock_response)
    )

    json_data = _request_chart_json(url)
    assert json_data == mock_response
    mock_requests.assert_called_once_with("https://example.com/data/chart.json")


def test_download(mocker, mock_response):
    url = "https://example.com"
    mocker.patch("requests.get", return_value=Mock(json=lambda: mock_response))

    expected_index = pd.to_datetime([1620000000000, 1620003600000], unit="ms")
    expected_df = pd.DataFrame(
        {
            "chart1": pd.to_numeric([1.1, 1.2], errors="coerce"),
            "chart2": pd.to_numeric([2.1, 2.2], errors="coerce"),
        },
        index=expected_index,
    )
    expected_df.index.name = "Date"

    result_df = _download(url)

    pd.testing.assert_frame_equal(result_df, expected_df)


@pytest.mark.parametrize(
    "url, expected_columns",
    [
        (
            "https://woocharts.com/bitcoin-price-models/",
            ["market", "realised", "delta", "top_", "vwap", "wma200", "cvdd"],
        ),
        (
            "https://woocharts.com/bitcoin-congestion/",
            [
                "volume",
                "size_block",
                "size_total",
                "confirm_time",
                "adoption",
                "mempool",
            ],
        ),
    ],
)
def test_woocharts(url, expected_columns):
    data = _download(url)

    assert isinstance(data, pd.DataFrame)
    assert isinstance(data.index, pd.DatetimeIndex)
    import numpy as np

    assert all(np.issubdtype(dtype, float) for dtype in data.dtypes)

    assert all(col in data.columns for col in expected_columns)
