# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Application
```bash
uv run python main.py      # Run the main script
```

### Managing Dependencies
```bash
uv sync                    # Install/sync all dependencies from lock file
uv add <package>          # Add a new dependency
uv remove <package>       # Remove a dependency
```

## Architecture

This is a simple Python financial analysis tool that fetches stock data using the Yahoo Finance API.

### Project Structure
- **main.py**: Single-file application that fetches and displays stock ticker data
- **pyproject.toml**: Modern Python project configuration using UV package manager
- **Python 3.12**: Required version (specified in .python-version)

### Key Dependencies
- **yfinance**: Primary dependency for fetching financial data from Yahoo Finance
- **pandas**: Used for data manipulation (comes as transitive dependency)

### Current Implementation
The application currently:
1. Creates a YFinance Ticker object for AAPL (Apple stock)
2. Fetches 6 months of historical data
3. Displays the first 5 rows using pandas DataFrame

### Development Notes
- Uses UV as the package manager (modern Python packaging tool)
- No test framework currently configured
- No linting or formatting tools set up
- Early prototype stage with hardcoded ticker symbol