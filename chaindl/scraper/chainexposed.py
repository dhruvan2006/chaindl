import re
import json

import pandas as pd
from bs4 import BeautifulSoup

from . import utils


def _download(url):
    content = utils._get_page_content(url)
    soup = BeautifulSoup(content, "html.parser")
    scripts = soup.find_all("script")

    dfs = _extract_data_from_scripts(scripts)

    merged_df = pd.concat(dfs, axis=1, join="outer")
    return merged_df


def _extract_data_from_scripts(scripts):
    dfs = []

    for script in scripts:
        if script.string and "Plotly.newPlot" in script.string:
            matches = re.findall(
                r"var trace\d+ =\s*{\s*x:\s*(\[[^\]]*\]),\s*y:\s*(\[[^\]]*\]),.*?name:\s*\'(.*?)\'",
                script.string,
                re.DOTALL,
            )
            for match in matches:
                x_data, y_data, name = match
                name = name.replace("\\u003c", "<").replace("\\u003e", ">")
                x = json.loads(x_data)
                y = json.loads(y_data)

                df = pd.DataFrame(
                    {name: pd.to_numeric(y, errors="coerce")},
                    index=pd.to_datetime(pd.to_datetime(x).date),
                )
                df.index.name = "Date"
                dfs.append(df)

    return dfs
