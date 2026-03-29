import requests
import pandas as pd

from .utils import _join_url

def _download(url):
    data = _request_chart_json(url)
    
    dfs = []
    for key, value in data.items():
        name = key
        x = value['x']
        y = value['y']

        df = pd.DataFrame({ name: pd.to_numeric(y, errors='coerce') }, index=pd.to_datetime(x, unit='ms'))
        df.index.name = 'Date'
        dfs.append(df)
    
    merged_df = pd.concat(dfs, axis=1, join='outer', sort=True)
    return merged_df

def _request_chart_json(url):
    json_url = _join_url(url, "data/chart.json")
    response = requests.get(json_url)
    return response.json()
