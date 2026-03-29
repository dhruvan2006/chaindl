import pandas as pd
import pytest

from chaindl.scraper.blockchain import _download


@pytest.mark.parametrize(
    "url, expected_columns",
    [
        (
            "https://www.blockchain.com/explorer/charts/avg-block-size",
            ["Market Price (USD)", "Average Block Size"],
        ),
        (
            "https://www.blockchain.com/explorer/charts/market-price",
            ["Market Price (USD)"],
        ),
    ],
)
def test_blockchain_download(url, expected_columns):
    data = _download(url)

    assert isinstance(data, pd.DataFrame)
    assert isinstance(data.index, pd.DatetimeIndex)

    print(data)
    assert all(col in data.columns for col in expected_columns)
