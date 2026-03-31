import re
import json
import pandas as pd
from seleniumbase import SB


def _download(url, xvfb=None):
    content = _get_script_content_seleniumbase(url, xvfb)
    if not content:
        raise ValueError(
            f"Failed to retrieve any script content from {url}. Likely blocked by CAPTCHA."
        )

    traces = _get_traces(content)
    if not traces:
        raise ValueError(f"No data traces found in the page source for {url}.")

    dfs = []
    for trace in traces:
        name, x, y = _get_data(trace, content)
        if name and x and y:
            df = pd.DataFrame(
                {name: pd.to_numeric(y, errors="coerce")}, index=pd.to_datetime(x)
            )
            df.index.name = "Date"
            dfs.append(df)

    if not dfs:
        raise ValueError(
            f"Found traces but could not parse them into DataFrames for {url}."
        )

    return pd.concat(dfs, axis=1, join="outer")


def _get_script_content_seleniumbase(url, xvfb):
    with SB(uc=True, headless=False, xvfb=xvfb) as sb:
        sb.activate_cdp_mode(url)
        sb.uc_gui_click_captcha()
        sb.sleep(2)
        sb.uc_gui_click_captcha()
        sb.sleep(2)

        current_title = sb.get_title()
        if (
            not current_title
            or "Human Challenge" in current_title
            or "Just a moment" in current_title
        ):
            raise ValueError(
                "CAPTCHA challenge still detected after solving. Access may be blocked."
            )

        script_content = ""
        script_tags = sb.find_elements("script")
        for script_tag in script_tags:
            try:
                inner = script_tag.get_attribute("innerHTML")
                if inner and "trace" in inner:
                    script_content += inner + "\n"
            except Exception:
                continue
        return script_content


def _get_traces(content):
    trace_pattern = r"var\s+trace\d+\s*=\s*(\{.*?\}\s*);"
    traces = re.findall(trace_pattern, content, re.DOTALL)
    return traces


def _get_data(trace, content):
    x_pattern = r"x:\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*,"
    y_pattern = r"y:\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*,"
    name_pattern = r"name:\s*'([^']*)'"
    var_pattern = r"var\s+({name})\s*=\s*([^;]*);"

    name = ""
    x, y = [], []

    x_match = re.search(x_pattern, trace)
    y_match = re.search(y_pattern, trace)

    if x_match and y_match:
        x_var_name = x_match.group(1)
        y_var_name = y_match.group(1)

        x_var_pattern = var_pattern.format(name=x_var_name)
        y_var_pattern = var_pattern.format(name=y_var_name)

        x = re.search(x_var_pattern, content)
        y = re.search(y_var_pattern, content)

        if x and y:
            x = json.loads(x.group(2))
            y = json.loads(y.group(2))

            length = min(len(x), len(y))
            x = x[:length]
            y = y[:length]

            name_match = re.search(name_pattern, trace)
            if name_match:
                name = name_match.group(1)

    return name, x, y
