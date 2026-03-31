import re
from urllib.parse import urlparse, parse_qs
from curl_cffi import requests
import pandas as pd

SESSION = requests.Session()


def _parse_metric_path(url: str):
    """Convert Glassnode chart URL path into API metric path and asset."""
    o = urlparse(url)
    path = o.path.replace(".", "/")
    query_params = parse_qs(o.query)
    asset = query_params.get("a", ["BTC"])[0]

    try:
        _, charts, *prefix_parts, last_segment = path.split("/")
    except ValueError:
        raise ValueError(f"Invalid Glassnode URL path: {path}")

    # Step 1: handle letter number boundaries: Min1Count -> Min_1Count
    number_adjusted = re.sub(r"([a-zA-Z])([0-9])", r"\1_\2", last_segment)
    # Step 2: handle Min_1Count -> Min_1_Count
    snake_case = re.sub(r"(?<!^)(?=[A-Z])", "_", number_adjusted).lower()
    new_path = "/".join(prefix_parts + [snake_case])
    return new_path, asset, snake_case


def _fetch_json(url: str):
    """Fetch JSON from a URL with session handling and error checking."""
    resp = SESSION.get(url)
    resp.raise_for_status()
    try:
        return resp.json()
    except ValueError:
        raise ValueError(f"Failed to parse JSON from {url}: {resp.text}")


def _process_metric_json(json_data, column_name: str):
    """Convert Glassnode metric JSON into a clean DataFrame."""
    df = pd.DataFrame(json_data)

    if "o" in df.columns:
        # Expand nested object
        columns = list(df["o"].iloc[0].keys())
        expanded_df = pd.DataFrame([row["o"] for row in json_data])
        expanded_df["Date"] = df["t"]
        cols = ["Date"] + columns
        expanded_df = expanded_df[cols]
        expanded_df.index = pd.to_datetime(expanded_df["Date"], unit="s")
        expanded_df = expanded_df.drop(columns=["Date"])
        return expanded_df
    else:
        df.rename(columns={"t": "Date", "v": column_name}, inplace=True)
        df.index = pd.to_datetime(df["Date"], unit="s")
        df = df.drop(columns=["Date"])
        return df


def _download(url: str, include_price: bool = True) -> pd.DataFrame:
    try:
        metric_path, asset, snake_case = _parse_metric_path(url)

        # Fetch cookies
        SESSION.get(url)

        # Fetch metric
        api_url = f"https://api.glassnode.com/v1/metrics/{metric_path}?a={asset}&referrer=charts"
        json_data = _fetch_json(api_url)

        if "requiredPlan" in json_data:
            raise ValueError(f"Metric {snake_case} is not available on the free plan.")

        df = _process_metric_json(json_data, snake_case)

        # Optionally fetch USD price
        if include_price:
            price_api = f"https://api.glassnode.com/v1/metrics/market/price_usd_close?a={asset}&referrer=charts"
            json_price = _fetch_json(price_api)
            df_price = pd.DataFrame(json_price)
            df_price.rename(columns={"t": "Date", "v": "price_usd_close"}, inplace=True)
            df_price.index = pd.to_datetime(df_price["Date"], unit="s")
            df_price = df_price.drop(columns=["Date"])
            df = df.join(df_price, how="outer")

        return df

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Network error while fetching Glassnode metric: {e}")
    except ValueError as e:
        raise RuntimeError(f"Data error: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}")
