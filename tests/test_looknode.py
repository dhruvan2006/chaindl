import pandas as pd
import pytest

from chaindl.scraper.looknode import _download

@pytest.mark.parametrize("url, expected_columns", [
    (
        "https://www.looknode.com/charts?chartId=reserveRisk",
        ["v1"]
    ),
    (
        "https://www.looknode.com/charts?chartId=ageOnSale",
        ["v1", "v2", "v3", "v4", "v5", "v6", "v7", "v8", "v9", "v10", "v11", "v12", "v13"]
    )
])
def test_looknode_download(url, expected_columns):
    data = _download(url)

    assert isinstance(data, pd.DataFrame)
    assert isinstance(data.index, pd.DatetimeIndex)

    print(data)
    assert all(col in data.columns for col in expected_columns)