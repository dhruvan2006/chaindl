import pytest
import pandas as pd
from chaindl.scraper.dune import _download


def test_download_dune():
    url = "https://dune.com/queries/3265994/5466888"
    df = _download(url, xvfb=None)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "date" in df.columns
    assert "BTC_Price" in df.columns
    assert "mv_ratio" in df.columns


def test_download_dashboard():
    url = "https://dune.com/cryptokoryo/crypto-buy-signal"
    with pytest.raises(ValueError, match="URL is not a valid Dune query URL"):
        _download(url, xvfb=None)
