# Multi-Asset Portfolio Analysis

A reproducible Python backtest of a diversified nine-asset allocation, with quarterly rebalancing, explicit transaction costs and detailed performance, drawdown and tail-risk analytics.

## Research design

| Parameter | Implementation |
|---|---|
| Historical window | 2017–2026 |
| Assets | 9 ETF and index proxies |
| Rebalancing | Quarterly |
| Transaction costs | 5 bps on turnover |
| Starting NAV | 100 |
| Analytics | 20+ performance and risk metrics |

### Target allocation

| Sleeve | Weight |
|---|---:|
| MSCI World | 17.78% |
| World Quality Dividend | 8.89% |
| Europe equities | 11.11% |
| Asia-Pacific equities | 6.67% |
| Euro government bonds | 11.11% |
| US Treasuries | 11.11% |
| US inflation-linked bonds | 11.11% |
| Gold | 11.11% |
| US real estate | 11.11% |

## Latest committed output

| Metric | Result |
|---|---:|
| Total return | 82.71% |
| CAGR | 7.36% |
| Annualised volatility | 7.98% |
| Sharpe ratio | 0.93 |
| Maximum drawdown | -15.56% |

These figures reproduce the latest summary file committed to the repository. They are historical backtest outputs, not forecasts.

![Portfolio NAV](reports/figures/fig_nav.png)

![Portfolio drawdown](reports/figures/fig_drawdown.png)

## Pipeline

1. Download adjusted historical prices for the nine proxies.
2. Align the dataset to dates shared by every asset.
3. Calculate daily simple returns.
4. Apply target weights with quarterly rebalancing.
5. Deduct 5 bps from portfolio turnover.
6. Calculate performance, drawdown, distribution and tail-risk metrics.
7. Export charts and CSV tables to `reports/`.

## Reproduce the analysis

```bash
git clone https://github.com/KenaelMartini/multi-asset-portfolio-analysis.git
cd multi-asset-portfolio-analysis
python -m venv .venv
```

Activate the environment and install the minimal dependencies:

```bash
# Windows
.venv\Scripts\activate
python -m pip install pandas numpy matplotlib yfinance

# macOS / Linux
source .venv/bin/activate
python -m pip install pandas numpy matplotlib yfinance
```

Download the data and run the nine-asset backtest:

```bash
python scripts/download_data_kmco.py
python main_KMCO.py
```

## Repository structure

```text
data/                    Historical price matrices
scripts/                 Data-download scripts
src/                     Backtest engine, metrics and reporting modules
reports/figures/         Generated NAV, drawdown and return charts
reports/tables/          Generated summary and monthly-return tables
main_KMCO.py             Nine-asset portfolio analysis
main.py                  Simpler four-asset reference allocation
```

## Development approach

This project was developed through an AI-assisted workflow. I directed the allocation assumptions, rebalancing and cost methodology, iteratively evaluated and integrated generated code, and remained responsible for data validation, metric verification, interpretation and final outputs.

## Limitations

- The universe uses tradable proxies and does not model every implementation constraint.
- Results are sensitive to the common-history window, data source and rebalancing assumptions.
- Taxes, bid-ask spreads, market impact and currency-hedging costs are not fully modelled.
- Historical performance does not predict future results.

## Disclaimer

For educational and independent research purposes only. Nothing in this repository constitutes financial advice, an investment recommendation or a regulated financial service.