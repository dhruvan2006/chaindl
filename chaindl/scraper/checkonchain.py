import re
import json
import base64
import struct

import pandas as pd
from bs4 import BeautifulSoup

from . import utils


def _download(url):
    content = utils._get_page_content(url)
    soup = BeautifulSoup(content, "html.parser")
    scripts = soup.find_all("script")

    dfs = _extract_data_from_scripts(scripts)

    merged_df = pd.concat(dfs, axis=1, join="outer", sort=True)
    return merged_df


def _extract_data_from_scripts(scripts):
    dfs = []
    for script in scripts:
        if script.string and "Plotly.newPlot" in script.string:
            matches = re.findall(
                r'"name":\s*"([^"]*)"\s*,.*?"x":\s*(\[.*?\])\s*,\s*"y":\s*({.*?}|\[.*?\])',
                script.string,
                re.DOTALL,
            )
            for match in matches:
                name, x_data, y_data = match
                name = name.replace("\\u003c", "<").replace("\\u003e", ">")
                x = json.loads(x_data)
                y_raw = json.loads(y_data)

                if isinstance(y_raw, dict) and "bdata" in y_raw:
                    # Decode base64 string to binary, then to float64 using struct
                    binary_data = base64.b64decode(y_raw["bdata"])
                    count = len(binary_data) // 8  # 8 bytes per float64
                    y = list(struct.unpack(f"{count}d", binary_data))
                else:
                    y = y_raw

                df = pd.DataFrame(
                    {name: pd.to_numeric(y, errors="coerce")},
                    index=pd.to_datetime(pd.to_datetime(x, format="mixed").date),
                )
                df.index.name = "Date"
                df = df.loc[
                    ~df.index.duplicated(keep="first")
                ]  # TODO: Give user option to either choose drop dupes or take avg
                dfs.append(df)

    return dfs
