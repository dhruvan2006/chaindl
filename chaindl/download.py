import pandas as pd

from . import scraper

def download(url, start=None, end=None, **kwargs):
    """
    Downloads cryptocurrency data from the specified URL and returns it as a pandas DataFrame.

    This function supports various data sources and handles specific URLs to retrieve data from each.

    Args:
        url (str): The URL from which to download the data. It must match one of the known data sources.
        start (str, optional): The start date for slicing the DataFrame. Must be in a format recognized by pandas (e.g., 'YYYY-MM-DD').
        end (str, optional): The end date for slicing the DataFrame. Must be in a format recognized by pandas (e.g., 'YYYY-MM-DD').
        **kwargs: Additional keyword arguments to pass to specific scraper methods.\n
            email and password needs to be passed for Cryptoquant\n
            sbr_webdriver needs to be passed for using a remote browser proxy (Eg: BrightData, etc.)

    Returns:
        pd.DataFrame: A DataFrame containing the downloaded data. The DataFrame index is datetime.

    Raises:
        ValueError: If the provided URL does not match any known data sources.

    Supported Data Sources:
        - CheckOnChain: "https://charts.checkonchain.com"
        - ChainExposed: "https://chainexposed.com"
        - BitBo: "https://charts.bitbo.io"
        - WooCharts: "https://woocharts.com"
        - CryptoQuant: "https://cryptoquant.com"
        - Bitcoin Magazine Pro: "https://www.bitcoinmagazinepro.com"
        - Blockchain.com: "https://www.blockchain.com/explorer/charts"
        - Glassnode: "https://studio.glassnode.com/charts"
        - The Block: "https://www.theblock.co"
        - Dune: "https://dune.com"
        - Looknode: "https://www.looknode.com"

    Example:
        >>> df = download("https://charts.checkonchain.com/path/to/indicator")
        >>> df_filtered = download("https://charts.checkonchain.com/path/to/indicator", start='2023-01-01', end='2023-12-31')
        >>> cryptoquant = download("https://cryptoquant.com/path/to/indicator", email=email, password=password)
    """
    CHECKONCHAIN_BASE_URL = "https://charts.checkonchain.com"
    CHAINEXPOSED_BASE_URL = "https://chainexposed.com"
    BITBO_BASE_URL = "https://charts.bitbo.io"
    WOOCHARTS_BASE_URL = "https://woocharts.com"
    CRYPTOQUANT_BASE_URL = "https://cryptoquant.com"
    BITCOINMAGAZINEPRO_BASE_URL = "https://www.bitcoinmagazinepro.com"
    BLOCKCHAIN_BASE_URL = "https://www.blockchain.com/explorer/charts"
    GLASSNODE_BASE_URL = "https://studio.glassnode.com/charts"
    THEBLOCK_BASE_URL = "https://www.theblock.co"
    DUNE_BASE_URL = "https://dune.com"
    LOOKNODE_BASE_URL = "https://www.looknode.com"

    data = pd.DataFrame()

    if url.startswith(CHECKONCHAIN_BASE_URL):
        data = scraper.checkonchain._download(url)
    elif url.startswith(CHAINEXPOSED_BASE_URL):
        data = scraper.chainexposed._download(url)
    elif url.startswith(BITBO_BASE_URL):
        data = scraper.bitbo._download(url, **kwargs)
    elif url.startswith(WOOCHARTS_BASE_URL):
        data = scraper.woocharts._download(url)
    elif url.startswith(CRYPTOQUANT_BASE_URL):
        data = scraper.cryptoquant._download(url, **kwargs)
    elif url.startswith(BITCOINMAGAZINEPRO_BASE_URL):
        data = scraper.bitcoinmagazinepro._download(url, **kwargs)
    elif url.startswith(BLOCKCHAIN_BASE_URL):
        data = scraper.blockchain._download(url, **kwargs)
    elif url.startswith(GLASSNODE_BASE_URL):
        data = scraper.glassnode._download(url, **kwargs)
    elif url.startswith(THEBLOCK_BASE_URL):
        data = scraper.theblock._download(url)
    elif url.startswith(DUNE_BASE_URL):
        data = scraper.dune._download(url)
    elif url.startswith(LOOKNODE_BASE_URL):
        data = scraper.looknode._download(url)
    else:
        raise ValueError("Unsupported source. Find the list of supported websites here: https://chaindl.readthedocs.io/")
    
    if pd.api.types.is_datetime64_any_dtype(data.index):
        if start:
            data = data.loc[start:]
        if end:
            data = data.loc[:end]

    return data
