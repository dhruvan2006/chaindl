import json
import pandas as pd
from seleniumbase import SB


def _download(url, proxy=None, xvfb=None):
    """Main entry point to fetch and process data."""
    data = _intercept_network_requests(url, proxy, xvfb)
    # Extract the plotly figure data from the Dash response
    traces = data["response"]["chart"]["figure"]["data"]
    dfs = _create_dataframes(traces)
    merged_df = pd.concat(dfs, axis=1, join="outer")
    return merged_df


def _create_dataframes(traces):
    """Processes Plotly traces into a list of DataFrames."""
    dfs = []
    for trace in traces:
        name = trace.get("name", "unnamed")
        x = trace.get("x", [])
        y = trace.get("y", [])

        length = min(len(x), len(y))
        x = x[:length]
        y = y[:length]

        df = pd.DataFrame(
            {name: pd.to_numeric(y, errors="coerce")},
            index=pd.to_datetime(pd.to_datetime(x, format="mixed").date),
        )

        df = df[~df.index.duplicated(keep="first")]
        df.index.name = "Date"
        dfs.append(df)
    return dfs


def _intercept_network_requests(url, proxy, xvfb, timeout=10):
    """Uses SeleniumBase CDP to capture Dash network responses."""
    target_url_fragment = "_dash-update-component"

    with SB(headless=True, uc_cdp_events=True, proxy=proxy, xvfb=xvfb) as sb:
        events = []

        sb.uc_open_with_reconnect(url, 1)
        sb.driver.add_cdp_listener(
            "Network.requestWillBeSent",
            lambda data: (
                events.append(data)
                if target_url_fragment
                in data.get("params", {}).get("request", {}).get("url", "")
                else None
            ),
        )

        request_id = None
        for _ in range(2 * timeout):
            if events:
                request_id = events[0].get("params", {}).get("requestId")
                break
            sb.sleep(0.5)
        if not request_id:
            raise ValueError("Dash update request not found.")

        try:
            result = sb.driver.execute_cdp_cmd(
                "Network.getResponseBody", {"requestId": request_id}
            )
            body_content = result.get("body", "{}")
            return json.loads(body_content)
        except Exception as e:
            raise Exception(f"Failed to retrieve response body: {str(e)}")
