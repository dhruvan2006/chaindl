import pandas as pd

from . import scraper


def download(url, start=None, end=None, xvfb=None):
    """
    Downloads cryptocurrency data from the specified URL and returns it as a pandas DataFrame.

    This function supports various data sources and handles specific URLs to retrieve data from each.

    Args:
        url (str): The URL from which to download the data. It must match one of the known data sources.
        start (str, optional): The start date for slicing the DataFrame. Must be in a format recognized by pandas (e.g., 'YYYY-MM-DD').
        end (str, optional): The end date for slicing the DataFrame. Must be in a format recognized by pandas (e.g., 'YYYY-MM-DD').
        xvfb (bool, optional): Whether to use Xvfb for headless browser scraping. Required for certain sources that may trigger CAPTCHAs (e.g., BitBo, Dune). Defaults to None.

    Returns:
        pd.DataFrame: A DataFrame containing the downloaded data. The DataFrame index is datetime.

    Raises:
        ValueError: If the provided URL does not match any known data sources.

    Supported Data Sources:
        - CheckOnChain: "https://charts.checkonchain.com"
        - ChainExposed: "https://chainexposed.com"
        - BitBo: "https://charts.bitbo.io"
        - WooCharts: "https://woocharts.com"
        - Blockchain.com: "https://www.blockchain.com/explorer/charts"
        - Glassnode: "https://studio.glassnode.com/charts"
        - The Block: "https://www.theblock.co"
        - Dune: "https://dune.com"

    Example:
        >>> df = download("https://charts.checkonchain.com/path/to/indicator")
        >>> df_filtered = download("https://charts.checkonchain.com/path/to/indicator", start='2023-01-01', end='2023-12-31')
        >>> df_proxy = download("https://charts.checkonchain.com/path/to/indicator", proxy='http://user:pass@host:port')
    """
    CHECKONCHAIN_BASE_URL = "https://charts.checkonchain.com"
    CHAINEXPOSED_BASE_URL = "https://chainexposed.com"
    BITBO_BASE_URL = "https://charts.bitbo.io"
    WOOCHARTS_BASE_URL = "https://woocharts.com"
    BLOCKCHAIN_BASE_URL = "https://www.blockchain.com/explorer/charts"
    GLASSNODE_BASE_URL = "https://studio.glassnode.com/charts"
    THEBLOCK_BASE_URL = "https://www.theblock.co"
    DUNE_BASE_URL = "https://dune.com"
    BMPRO_BASE_URL = "https://www.bitcoinmagazinepro.com"

    data = pd.DataFrame()

    if url.startswith(CHECKONCHAIN_BASE_URL):
        data = scraper.checkonchain._download(url)
    elif url.startswith(CHAINEXPOSED_BASE_URL):
        data = scraper.chainexposed._download(url)
    elif url.startswith(BITBO_BASE_URL):
        data = scraper.bitbo._download(url, xvfb=xvfb)
    elif url.startswith(WOOCHARTS_BASE_URL):
        data = scraper.woocharts._download(url)
    elif url.startswith(BLOCKCHAIN_BASE_URL):
        data = scraper.blockchain._download(url)
    elif url.startswith(GLASSNODE_BASE_URL):
        data = scraper.glassnode._download(url)
    elif url.startswith(THEBLOCK_BASE_URL):
        data = scraper.theblock._download(url)
    elif url.startswith(DUNE_BASE_URL):
        data = scraper.dune._download(url, xvfb=xvfb)
    elif url.startswith(BMPRO_BASE_URL):
        data = scraper.bmpro._download(url, xvfb=xvfb)
    else:
        raise ValueError(
            "Unsupported source. Find the list of supported websites here: https://chaindl.readthedocs.io/"
        )

    if pd.api.types.is_datetime64_any_dtype(data.index):
        if start:
            data = data.loc[start:]
        if end:
            data = data.loc[:end]

    return data
