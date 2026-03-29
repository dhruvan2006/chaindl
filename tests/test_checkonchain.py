import pytest
import pandas as pd
from chaindl.scraper.checkonchain import _download
from chaindl.scraper.checkonchain import _extract_data_from_scripts
from chaindl.scraper import utils


def test_extract_data_from_scripts():
    scripts = [
        type(
            "",
            (object,),
            {
                "string": """Plotly.newPlot("plot", [{
            "name": "Price",
            "x": ["2024-09-30", "2024-10-01", "2024-10-02"],
            "y": [1, 2, 3]
        }]);"""
            },
        )()
    ]

    expected_data = pd.DataFrame(
        {"Price": [1, 2, 3]},
        index=pd.to_datetime(["2024-09-30", "2024-10-01", "2024-10-02"]).astype(
            "datetime64[s]"
        ),
    )
    expected_data.index.name = "Date"

    dfs = _extract_data_from_scripts(scripts)

    pd.testing.assert_frame_equal(dfs[0], expected_data)


def test_checkonchain_mocked(monkeypatch):
    def mock_get_page_content(url):
        return """
        <script>
        Plotly.newPlot("plot", [{
            "name": "Price",
            "x": ["2024-09-30", "2024-10-01", "2024-10-02"],
            "y": [1, 2, 3]
        }]);
        </script>
        """

    monkeypatch.setattr(utils, "_get_page_content", mock_get_page_content)

    url = "https://charts.checkonchain.com/test"
    data = _download(url)

    expected_data = pd.DataFrame(
        {"Price": [1, 2, 3]},
        index=pd.to_datetime(["2024-09-30", "2024-10-01", "2024-10-02"]).astype(
            "datetime64[s]"
        ),
    )
    expected_data.index.name = "Date"

    pd.testing.assert_frame_equal(data, expected_data)


@pytest.mark.parametrize(
    "url, expected_columns",
    [
        (
            "https://charts.checkonchain.com/btconchain/pricing/pricing_mayermultiple_zscore/pricing_mayermultiple_zscore_light.html",
            [
                "Mayer Multiple Z",
                "200DMA",
                "Price",
                "1.5sd",
                "1.0sd",
                "-1.0sd",
                "-1.5sd",
            ],
        ),
        (
            "https://charts.checkonchain.com/btconchain/realised/sopr/sopr_light.html",
            ["Price", "Spent Output Profit Ratio (SOPR)", "SOPR 7D-EMA"],
        ),
    ],
)
def test_real_checkonchain_download(url, expected_columns):
    data = _download(url)

    assert isinstance(data, pd.DataFrame)
    assert isinstance(data.index, pd.DatetimeIndex)
    import numpy as np

    assert all(np.issubdtype(dtype, float) for dtype in data.dtypes)

    assert all(col in data.columns for col in expected_columns)
