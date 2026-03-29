import pandas as pd
import pytest
from unittest.mock import patch
from chaindl import download

mocked_data_with_dates = pd.DataFrame(
    {"data": [1, 2, 3, 4, 5]}, index=pd.date_range(start="2023-01-01", periods=5)
)

mocked_data = {
    "checkonchain": mocked_data_with_dates,
    "chainexposed": mocked_data_with_dates,
    "bitbo": mocked_data_with_dates,
    "woocharts": mocked_data_with_dates,
    "bmpro": mocked_data_with_dates,
}


@pytest.mark.parametrize(
    "url, expected_data, provider",
    [
        (
            "https://charts.checkonchain.com/some_data",
            mocked_data["checkonchain"],
            "checkonchain",
        ),
        (
            "https://chainexposed.com/some_data",
            mocked_data["chainexposed"],
            "chainexposed",
        ),
        ("https://charts.bitbo.io/some_data", mocked_data["bitbo"], "bitbo"),
        ("https://woocharts.com/some_data", mocked_data["woocharts"], "woocharts"),
        (
            "https://www.bitcoinmagazinepro.com/some_data",
            mocked_data["bmpro"],
            "bmpro",
        ),
    ],
)
def test_download_valid_urls(url, expected_data, provider):
    with patch(f"chaindl.scraper.{provider}._download", return_value=expected_data):
        result = download(url)
        pd.testing.assert_frame_equal(result, expected_data)


def test_download_invalid_url():
    invalid_url = "https://unknownsource.com/some_data"
    with pytest.raises(ValueError, match="Unsupported source"):
        download(invalid_url)


@pytest.mark.parametrize(
    "url, start, end, expected_data",
    [
        (
            "https://charts.checkonchain.com/some_data",
            "2023-01-02",
            "2023-01-04",
            pd.DataFrame(
                {"data": [2, 3, 4]}, index=pd.date_range(start="2023-01-02", periods=3)
            ),
        ),
        (
            "https://charts.checkonchain.com/some_data",
            "2023-01-01",
            None,
            pd.DataFrame(
                {"data": [1, 2, 3, 4, 5]},
                index=pd.date_range(start="2023-01-01", periods=5),
            ),
        ),
        (
            "https://charts.checkonchain.com/some_data",
            None,
            "2023-01-03",
            pd.DataFrame(
                {"data": [1, 2, 3]}, index=pd.date_range(start="2023-01-01", periods=3)
            ),
        ),
    ],
)
def test_download_date_filtration(url, start, end, expected_data):
    with patch(
        "chaindl.scraper.checkonchain._download",
        return_value=mocked_data["checkonchain"],
    ):
        result = download(url, start=start, end=end)
        pd.testing.assert_frame_equal(result, expected_data)
