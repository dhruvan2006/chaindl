import json
import pandas as pd
from seleniumbase import SB
from urllib.parse import urlparse


def _download(url: str, proxy=None, xvfb=None) -> pd.DataFrame:
    # Parse the query ID from URL
    parsed = urlparse(url)
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2 or parts[0] != "queries":
        raise ValueError(
            "URL is not a valid Dune query URL. Follow the guide at: https://chaindl.readthedocs.io/#dune-dune-com"
        )

    target_url_fragment = "core-api.dune.com/public/execution"

    with SB(
        undetectable=True, headless=False, uc_cdp_events=True, proxy=proxy, xvfb=xvfb
    ) as sb:
        events = []

        sb.uc_open_with_reconnect(url, 2)
        sb.driver.add_cdp_listener(
            "Network.requestWillBeSent", lambda data: events.append(data)
        )
        sb.sleep(3)

        # Get requestID
        request_id = None
        for event in reversed(events):
            if event.get("method") == "Network.requestWillBeSent":
                params = event.get("params", {})
                request = params.get("request", {})
                request_url = request.get("url", "")

                if target_url_fragment in request_url:
                    request_id = params.get("requestId")
                    break
        if not request_id:
            raise Exception(
                "Could not find the data execution request in browser logs."
            )

        # Get response
        result = sb.driver.execute_cdp_cmd(
            "Network.getResponseBody", {"requestId": request_id}
        )
        body_json = json.loads(result.get("body", "{}"))
        rows = body_json.get("execution_succeeded", {}).get("data", [])
        df = pd.DataFrame(rows)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        return df
