import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from chaindl.scraper.bitcoinmagazinepro import _download, _create_dataframes, _intercept_network_requests

@pytest.fixture
def mock_data():
    return {
        'response': {
            'chart': {
                'figure': {
                    'data': [
                        {
                            'name': 'Series1',
                            'x': ['2023-01-01', '2023-01-02', '2023-01-03'],
                            'y': [1, 2, 3],
                            'line': {}
                        },
                        {
                            'name': 'Series2',
                            'x': ['2023-01-01', '2023-01-02', '2023-01-03'],
                            'y': [4, 5, 6],
                            'line': {}
                        }
                    ]
                }
            }
        }
    }

def test_create_dataframes(mock_data):
    traces = mock_data['response']['chart']['figure']['data']
    dfs = _create_dataframes(traces)

    expected_df1 = pd.DataFrame({
        'Series1': [1, 2, 3]
    }, index=pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']).astype('datetime64[s]'))
    expected_df1.index.name = 'Date'

    expected_df2 = pd.DataFrame({
        'Series2': [4, 5, 6]
    }, index=pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']).astype('datetime64[s]'))
    expected_df2.index.name = 'Date'

    pd.testing.assert_frame_equal(dfs[0], expected_df1)
    pd.testing.assert_frame_equal(dfs[1], expected_df2)

@pytest.mark.parametrize("url, expected_columns", [
    (
        "https://www.bitcoinmagazinepro.com/charts/sopr-spent-output-profit-ratio/",
        ['BTC Price', 'SOPR']
    ),
    (
        "https://www.bitcoinmagazinepro.com/charts/stock-to-flow-model/",
        ['BTC Price', 'Stock/Flow (365d average)', 'Model Variance', 'Halving Dates']
    )
])
def test_bitbo_download(url, expected_columns):
    data = _download(url)

    assert isinstance(data, pd.DataFrame)
    assert isinstance(data.index, pd.DatetimeIndex)
    assert all(data.dtypes == float)

    assert all(col in data.columns for col in expected_columns)
