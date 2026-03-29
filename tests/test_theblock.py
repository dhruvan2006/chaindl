from chaindl.scraper.theblock import _download


def test_transactions_on_the_bitcoin_network():
    url = "https://www.theblock.co/data/on-chain-metrics/bitcoin/transactions-on-the-bitcoin-network-daily"
    df = _download(url)
    assert "7DMA" in df.columns
    assert "Date" == df.index.name
    assert not df.empty
