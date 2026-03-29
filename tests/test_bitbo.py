import os
import pytest
import pandas as pd
from dotenv import load_dotenv
from chaindl.scraper.bitbo import _get_traces, _get_data, _download

load_dotenv()

sbr_webdriver = os.getenv('SBR_WEBDRIVER')

content = """
    var axis_x = ["2020-10-20","2020-10-21","2020-10-22"];
    var price_c = [11921.78,12813.11,12990.25];
    var sma200 = [9844.96,9874.65,9905.69];
    var sma1458 = [6650.14,6658.48,6666.94];
    var current = "2024-10-01";

    var trace1 = {
			type: "scatter",
			name: 'Price end of day',
			x: axis_x,
			y: price_c,
			line: {width: 2}
		};
    var trace2 = {
			type: "scatter",
			name: 'MA1458d',
			x: axis_x,
			y: sma1458,
			line: {width: 2}
		};
"""

def test_get_traces():
    traces = _get_traces(content)

    assert len(traces) == 2
    assert 'Price end of day' in traces[0]
    assert 'MA1458d' in traces[1]

def test_get_data():
    trace = '{\n\t\t\ttype: "scatter",\n\t\t\tname: \'Price end of day\',\n\t\t\tx: axis_x,\n\t\t\ty: price_c,\n\t\t\tline: {width: 2}\n\t\t}'
    
    name, x, y = _get_data(trace, content)

    assert name == 'Price end of day'
    assert x == ["2020-10-20","2020-10-21","2020-10-22"]
    assert y == [11921.78, 12813.11, 12990.25]

def test_download_data(monkeypatch):
    expected_df = pd.DataFrame({
        'Price end of day': [11921.78, 12813.11, 12990.25],
        'MA1458d': [6650.14, 6658.48, 6666.94]
    }, index=pd.to_datetime(["2020-10-20","2020-10-21","2020-10-22"]))
    expected_df.index.name = 'Date'

    import chaindl.scraper.bitbo as bitbo
    monkeypatch.setattr(bitbo, '_get_script_content_seleniumbase', lambda url: content)

    result_df = _download('test_url')

    pd.testing.assert_frame_equal(result_df, expected_df)


@pytest.mark.parametrize("url, expected_columns", [
    (
        "https://charts.bitbo.io/cycle-repeat/",
        ['MA1458d', 'MA200d', 'Price end of day']
    ),
    (
        "https://charts.bitbo.io/macd/",
        ['Price', 'MACD', 'Signal line']
    )
])
def test_bitbo_download_sb(url, expected_columns):
    data = _download(url)

    assert isinstance(data, pd.DataFrame)
    assert isinstance(data.index, pd.DatetimeIndex)
    assert all(data.dtypes == float)

    assert all(col in data.columns for col in expected_columns)
