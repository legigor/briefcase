# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Global goal
The gloabl goal is to create a financial assistent helping to build the stocks portfolio.

## Intermediate goals
- Download the historical data for the entire market from Yahoo Finance
- Conduct series of experiments to find the best strategies for portfolio optimization
- Implement a user-friendly interface for the financial assistant

## Current Goal
- Download the historical data for all possible stocks data for at least the past 5 years with daily frequency.
- Download key financial metrics (e.g., P/E ratio, market cap) for each stock.
- Store the collected data in a structured format (e.g., database, CSV files) for easy access and analysis into ./data directory.

## Commands

### Data Collection
```bash
# Test with 10 sample stocks
uv run python collect_data.py --test

# Run full market data collection
uv run python collect_data.py --full

# Download specific tickers
uv run python collect_data.py --tickers AAPL GOOGL MSFT
```

### Data Analysis
```bash
# Generate analysis report
uv run python analyze_data.py --report

# Analyze specific ticker
uv run python analyze_data.py --ticker AAPL

# Show top performers
uv run python analyze_data.py --top-performers 20

# Export to parquet format
uv run python analyze_data.py --export-parquet
```

### Managing Dependencies
```bash
uv sync                    # Install/sync all dependencies
uv add <package>          # Add a new dependency
uv remove <package>       # Remove a dependency
```

## Project Structure

```
briefcase/
├── research/              # Research and experimentation code
│   ├── data_collection/   # Market data download modules
│   ├── analysis/          # Data analysis tools
│   ├── experiments/       # Strategy experiments
│   └── notebooks/         # Jupyter notebooks
│
├── src/                   # Production code (future)
├── tests/                 # Test suites
├── docs/                  # Documentation
│
├── data/                  # Data storage (gitignored)
│   ├── raw/              # Raw downloaded data
│   │   ├── historical/   # Daily OHLCV data
│   │   ├── fundamentals/ # Financial metrics
│   │   └── metadata/     # Collection metadata
│   └── processed/        # Processed data
│
├── collect_data.py       # Convenience script for data collection
├── analyze_data.py       # Convenience script for analysis
└── main.py              # Simple demo script
```

## Architecture

This is a financial analysis platform for building and optimizing stock portfolios.

### Research Module
- **StockDataCollector**: Downloads historical data and fundamentals for 11,000+ stocks
- **DataAnalyzer**: Analyzes collected data, generates reports, identifies top performers
- Supports batch processing with resume capability
- Handles 5+ years of daily data for entire market (~12GB)

### Key Dependencies
- **yfinance**: Yahoo Finance API for market data
- **pandas/numpy**: Data manipulation and analysis
- **Python 3.12**: Required version

### Development Notes
- Uses UV as the package manager
- Research code isolated from future production code
- Data stored in structured format for easy access
- Supports incremental collection and error recovery