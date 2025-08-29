# chaindl

**Download crypto on-chain data with a single line of code.**

[![Build Passing](https://github.com/dhruvan2006/chaindl/actions/workflows/release.yml/badge.svg)](https://github.com/dhruvan2006/chaindl/actions/workflows/release.yml)
[![Tests Passing](https://github.com/dhruvan2006/chaindl/actions/workflows/tests.yml/badge.svg)](https://github.com/dhruvan2006/chaindl/actions/workflows/tests.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/chaindl)](https://pypi.org/project/chaindl/)
[![PyPI Downloads](https://static.pepy.tech/badge/ocfinance)](https://pypi.org/project/chaindl/)
[![GitHub License](https://img.shields.io/github/license/dhruvan2006/chaindl)](https://github.com/dhruvan2006/chaindl)

`chaindl` is a lightweight Python library that lets you fetch historical and live on-chain crypto data from multiple 
public sources in one step. Whether you want to analyze metrics from Bitcoin, Ethereum, or other chains, `chaindl` 
handles the heavy lifting so you can focus on insights.

## Why Use `chaindl`?

- **Fetch crypto on-chain data in one line** – no need for API keys or complicated setups.  
- **Fully free** – all functionality is available without subscription or payment.  
- **Ready for analysis** – data comes back as a `pandas.DataFrame`, so you can immediately manipulate, visualize, or model it.  
- **Save and share** – easily export data as CSV for offline use, Excel, or reporting.  
- **Multiple sources supported** – from Cryptoquant to CheckOnChain, get all your metrics without juggling different platforms.  
- **Focus on insights, not boilerplate** – `chaindl` handles parsing and formatting, so you spend less time on setup.

## Documentation: [https://chaindl.readthedocs.io/](https://chaindl.readthedocs.io/)

**Complete documentation is available at:** 
[https://chaindl.readthedocs.io/](https://chaindl.readthedocs.io/)

## Supported Websites
- [CheckOnChain](https://charts.checkonchain.com/)
- [ChainExposed](https://chainexposed.com/)
- [Woocharts](https://woocharts.com/)
- [Cryptoquant](https://cryptoquant.com/)
- [Bitbo Charts](https://charts.bitbo.io/)
- [Bitcoin Magazine Pro](https://www.bitcoinmagazinepro.com)
- [Blockchain.com](https://www.blockchain.com/explorer/charts)
- [Glassnode](https://studio.glassnode.com/charts/)
- [The Block](https://www.theblock.co/data/)
- [Dune](https://dune.com/)
- [Looknode] (https://www.looknode.com/)

## Installation
To install the `chaindl` package, use pip:
```bash
pip install chaindl
```

## Quick Start
To download the data of a chart, simply obtain the URL and pass it to the download function

```python
import chaindl

# Download data from a URL
data = chaindl.download("https://charts.checkonchain.com/btconchain/pricing/pricing_picycleindicator/pricing_picycleindicator_light.html")

# Export to CSV
data.to_csv('out.csv')

# Quick Plot
data.plot()
```

For advanced usage and examples with Cryptoquant and other sources, see the [documentation](https://chaindl.readthedocs.io/).
