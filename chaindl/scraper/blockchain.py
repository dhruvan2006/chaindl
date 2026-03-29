import requests
import pandas as pd


def _download(url, timespan="all", daysAverage="1d", include_price=True):
    """Allowed timespans: 30days, 90days, 180days, 1year, 3years, all"""
    metric = url.rstrip("/").split("/")[-1]
    api_url = f"https://api.blockchain.info/charts/{metric}"
    params = {
        "timespan": timespan,
        "sampled": "true",
        "metadata": "false",
        "daysAverageString": daysAverage,
        "format": "json",
    }
    response = requests.get(api_url, params=params)
    data = response.json()
    if "values" not in data or "name" not in data:
        raise ValueError(f"Invalid response for {metric} from Blockchain API.")
    values = data["values"]
    name = data["name"]

    df = pd.DataFrame(values)
    df = df.rename(columns={"x": "Date", "y": name or metric})
    df["Date"] = pd.to_datetime(df["Date"], unit="s")
    df = df.set_index("Date")

    if include_price and metric != "market-price":
        # Fetch bitcoin price
        btc_url = "https://api.blockchain.info/charts/market-price"
        btc_response = requests.get(btc_url, params=params)
        btc_data = btc_response.json()
        if "values" not in btc_data or "name" not in btc_data:
            raise ValueError("Invalid response for market price from Blockchain API.")
        btc_values = btc_data["values"]
        btc_df = pd.DataFrame(btc_values)
        btc_df = btc_df.rename(columns={"x": "Date", "y": "Market Price (USD)"})
        btc_df["Date"] = pd.to_datetime(btc_df["Date"], unit="s")
        btc_df = btc_df.set_index("Date")

        # Merge the dataframes on the Date index
        df = df.merge(btc_df, left_index=True, right_index=True, how="outer")

    return df
