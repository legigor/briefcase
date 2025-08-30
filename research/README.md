# Research Module

This module contains all research-related code for the financial assistant project.

## Structure

```
research/
├── data_collection/     # Scripts for downloading market data
│   ├── stock_data_collector.py  # Main data collection class
│   ├── run_full_collection.py   # Full collection script
│   └── yfinance_research.py     # YFinance capabilities research
│
├── analysis/           # Data analysis tools
│   └── data_analyzer.py        # Analysis and reporting tools
│
├── experiments/        # Experimental scripts and strategies
│   └── (future experiments)
│
└── notebooks/          # Jupyter notebooks for research
    └── (research notebooks)
```

## Quick Start

From the project root, use the convenience scripts:

```bash
# Test data collection with 10 stocks
uv run python collect_data.py --test

# Run full data collection
uv run python collect_data.py --full

# Analyze collected data
uv run python analyze_data.py --report

# Show top performers
uv run python analyze_data.py --top-performers 20

# Analyze specific ticker
uv run python analyze_data.py --ticker AAPL
```

## Data Organization

All data is stored in `data/` directory:

```
data/
├── raw/                # Raw downloaded data
│   ├── historical/     # Daily OHLCV data (CSV)
│   ├── fundamentals/   # Financial metrics (JSON)
│   └── metadata/       # Collection metadata
│
└── processed/          # Processed data (future)
    └── parquet/        # Optimized parquet files
```

## Research Workflow

1. **Data Collection**: Use `collect_data.py` to download market data
2. **Analysis**: Use `analyze_data.py` to explore the data
3. **Experiments**: Create scripts in `experiments/` for strategy testing
4. **Notebooks**: Use Jupyter notebooks for interactive research

## Module Usage

```python
# Using the data collector
from research.data_collection import StockDataCollector

collector = StockDataCollector()
collector.collect_all_data(tickers=['AAPL', 'GOOGL'])

# Using the analyzer
from research.analysis import DataAnalyzer

analyzer = DataAnalyzer()
report = analyzer.analyze_ticker('AAPL')
```