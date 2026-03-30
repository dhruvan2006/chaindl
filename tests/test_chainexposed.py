import pytest
import pandas as pd
from chaindl.scraper.chainexposed import _download
from chaindl.scraper.chainexposed import _extract_data_from_scripts
from chaindl.scraper import utils


def test_extract_data_from_scripts():
    scripts = [
        type(
            "",
            (object,),
            {
                "string": """Plotly.newPlotvar trace0 =
            {
            x: ["2012-01-01","2012-01-02","2012-01-03"],
            y: ["912.0","259.0","1375.0"],
            name: 'Price',
        }
                             
        Plotly.newPlot(target_target, data, layout, config); """
            },
        )()
    ]

    expected_data = pd.DataFrame(
        {"Price": [912.0, 259.0, 1375.0]},
        index=pd.to_datetime(["2012-01-01", "2012-01-02", "2012-01-03"]).astype(
            "datetime64[s]"
        ),
    )
    expected_data.index.name = "Date"

    dfs = _extract_data_from_scripts(scripts)

    pd.testing.assert_frame_equal(dfs[0], expected_data)


def test_chainexposed_mocked(monkeypatch):
    def mock_get_page_content(url, proxy):
        return """
        <script>
        Plotly.newPlotvar trace0 =
            {
            x: ["2012-01-01","2012-01-02","2012-01-03"],
            y: ["912.0","259.0","1375.0"],
            name: 'Price',
        }
                             
        Plotly.newPlot(target_target, data, layout, config); 
        </script>
        """

    monkeypatch.setattr(utils, "_get_page_content", mock_get_page_content)

    url = "https://chainexposed.com/test"
    data = _download(url)

    expected_data = pd.DataFrame(
        {"Price": [912.0, 259.0, 1375.0]},
        index=pd.to_datetime(["2012-01-01", "2012-01-02", "2012-01-03"]).astype(
            "datetime64[s]"
        ),
    )
    expected_data.index.name = "Date"

    pd.testing.assert_frame_equal(data, expected_data)


@pytest.mark.parametrize(
    "url, expected_columns",
    [
        (
            "https://chainexposed.com/ConsolidatedMetricCoinsDestroyed.html",
            ["Price", "Coins Destroyed", "Coins Destroyed 7d MA"],
        ),
        (
            "https://chainexposed.com/addressBandTotHUMPBACK.html",
            ["Price", "10000 and more (Humpbacks)"],
        ),
    ],
)
def test_real_chainexposed_download(url, expected_columns):
    data = _download(url)

    assert isinstance(data, pd.DataFrame)
    assert isinstance(data.index, pd.DatetimeIndex)
    assert all(pd.api.types.is_float_dtype(dtype) for dtype in data.dtypes)
    assert all(col in data.columns for col in expected_columns)
