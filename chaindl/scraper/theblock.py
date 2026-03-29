import json
import requests
import pandas as pd
from urllib.parse import urlparse


def _download(url):
    parsed = urlparse(url)
    parts = [p for p in parsed.path.split("/") if p]
    last_three = "/".join(parts[-3:])

    api = f"https://www.theblock.co/api/charts/chart/{last_three}"
    response = requests.get(api)
    response.raise_for_status()
    _json = response.json()
    jsonFile = _json.get("jsonFile", {}).get("data", {})
    jsonFile = json.loads(jsonFile)

    df = pd.concat(
        {
            series: pd.DataFrame(data["Data"]).set_index("Timestamp")["Result"]
            for series, data in jsonFile["Series"].items()
        },
        axis=1,
    )
    df.index = pd.to_datetime(df.index, unit="s")
    df.index.name = "Date"

    return df
