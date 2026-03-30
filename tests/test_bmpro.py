import pytest
import pandas as pd
from chaindl.scraper.bmpro import _download, _create_dataframes


def test_create_dataframes():
    mock_traces = [
        {"name": "Series1", "x": ["2023-01-01", "2023-01-02"], "y": [100, 200]}
    ]
    dfs = _create_dataframes(mock_traces)
    assert len(dfs) == 1
    assert dfs[0].iloc[0]["Series1"] == 100
    assert dfs[0].index.name == "Date"


@pytest.mark.parametrize(
    "url, expected_columns",
    [
        (
            "https://www.bitcoinmagazinepro.com/charts/sopr-spent-output-profit-ratio/",
            ["BTC Price", "SOPR"],
        ),
        (
            "https://www.bitcoinmagazinepro.com/charts/stock-to-flow-model/",
            [
                "BTC Price",
                "Stock/Flow (365d average)",
                "Model Variance",
                "Halving Dates",
            ],
        ),
    ],
)
def test_bitbo_download(url, expected_columns):
    data = _download(url, xvfb=None)

    assert isinstance(data, pd.DataFrame)
    assert isinstance(data.index, pd.DatetimeIndex)
    assert all(pd.api.types.is_float_dtype(dtype) for dtype in data.dtypes)

    assert all(col in data.columns for col in expected_columns)
