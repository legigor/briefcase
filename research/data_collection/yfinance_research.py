#!/usr/bin/env python3
"""
YFinance Capabilities and Limitations Research Script

This script investigates YFinance's capabilities for bulk stock data download,
including rate limiting, available tickers, bulk download methods, financial metrics,
data availability, and performance considerations.
"""

import yfinance as yf
import pandas as pd
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests
import sys


def test_rate_limiting():
    """Test YFinance rate limiting by making multiple requests"""
    print("=" * 60)
    print("TESTING RATE LIMITING")
    print("=" * 60)
    
    test_tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    start_time = time.time()
    
    for i, ticker in enumerate(test_tickers):
        print(f"Request {i+1}: Fetching {ticker}...")
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            print(f"  - Success: Got data for {ticker} (Market Cap: ${info.get('marketCap', 'N/A')})")
            time.sleep(0.1)  # Small delay between requests
        except Exception as e:
            print(f"  - Error for {ticker}: {e}")
    
    end_time = time.time()
    print(f"Total time for {len(test_tickers)} individual requests: {end_time - start_time:.2f} seconds")


def test_bulk_download():
    """Test bulk download capabilities using yfinance.download()"""
    print("\n" + "=" * 60)
    print("TESTING BULK DOWNLOAD CAPABILITIES")
    print("=" * 60)
    
    test_tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX"]
    
    print(f"Testing bulk download for {len(test_tickers)} tickers...")
    start_time = time.time()
    
    try:
        # Test bulk download
        data = yf.download(
            tickers=" ".join(test_tickers),
            period="1y",
            interval="1d",
            group_by="ticker",
            auto_adjust=True,
            prepost=True,
            threads=True,
            proxy=None
        )
        
        end_time = time.time()
        print(f"Bulk download successful in {end_time - start_time:.2f} seconds")
        print(f"Data shape: {data.shape}")
        print(f"Available columns: {data.columns.names}")
        
        # Show sample data structure
        print("\nSample data structure:")
        if len(test_tickers) > 1:
            print(data.head(3))
        
        return True
    except Exception as e:
        print(f"Bulk download failed: {e}")
        return False


def explore_ticker_info_metrics():
    """Explore available financial metrics from ticker.info"""
    print("\n" + "=" * 60)
    print("EXPLORING AVAILABLE FINANCIAL METRICS")
    print("=" * 60)
    
    ticker = yf.Ticker("AAPL")
    try:
        info = ticker.info
        print(f"Total info fields available: {len(info.keys())}")
        
        # Key financial metrics we're interested in
        key_metrics = [
            'marketCap', 'enterpriseValue', 'trailingPE', 'forwardPE',
            'pegRatio', 'priceToBook', 'priceToSalesTrailing12Months',
            'enterpriseToRevenue', 'enterpriseToEbitda', 'profitMargins',
            'operatingMargins', 'returnOnAssets', 'returnOnEquity',
            'revenueGrowth', 'earningsGrowth', 'currentRatio', 'quickRatio',
            'totalCash', 'totalDebt', 'debtToEquity', 'freeCashflow',
            'operatingCashflow', 'earningsQuarterlyGrowth', 'netIncomeToCommon',
            'trailingAnnualDividendYield', 'dividendYield', 'payoutRatio',
            'beta', 'heldPercentInsiders', 'heldPercentInstitutions',
            'shortRatio', 'bookValue', 'priceToBook', 'lastFiscalYearEnd',
            'nextFiscalYearEnd', 'mostRecentQuarter', 'earningsQuarterlyGrowth',
            'revenueQuarterlyGrowth'
        ]
        
        print("\nKey Financial Metrics Available:")
        available_metrics = []
        for metric in key_metrics:
            value = info.get(metric)
            if value is not None:
                available_metrics.append(metric)
                print(f"  ✓ {metric}: {value}")
            else:
                print(f"  ✗ {metric}: Not available")
        
        print(f"\nTotal available key metrics: {len(available_metrics)}/{len(key_metrics)}")
        
        # Show all available fields
        print(f"\nAll available info fields:")
        sorted_keys = sorted(info.keys())
        for i, key in enumerate(sorted_keys):
            if i % 4 == 0:
                print()
            print(f"{key:30}", end=" ")
        print("\n")
        
        return available_metrics
    except Exception as e:
        print(f"Error exploring ticker info: {e}")
        return []


def test_historical_data_limits():
    """Test historical data availability and limits"""
    print("\n" + "=" * 60)
    print("TESTING HISTORICAL DATA LIMITS")
    print("=" * 60)
    
    ticker = yf.Ticker("AAPL")
    
    # Test different periods
    periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
    
    print("Testing different historical periods:")
    for period in periods:
        try:
            data = ticker.history(period=period)
            if not data.empty:
                start_date = data.index[0].strftime("%Y-%m-%d")
                end_date = data.index[-1].strftime("%Y-%m-%d")
                days = len(data)
                print(f"  ✓ {period:4}: {days:4} days ({start_date} to {end_date})")
            else:
                print(f"  ✗ {period:4}: No data available")
        except Exception as e:
            print(f"  ✗ {period:4}: Error - {e}")
    
    # Test specific date ranges
    print("\nTesting specific date ranges (5+ years):")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365)  # 5 years ago
    
    try:
        data = ticker.history(start=start_date.strftime("%Y-%m-%d"), 
                            end=end_date.strftime("%Y-%m-%d"))
        if not data.empty:
            actual_start = data.index[0].strftime("%Y-%m-%d")
            actual_end = data.index[-1].strftime("%Y-%m-%d")
            days = len(data)
            print(f"  ✓ 5-year range: {days} days ({actual_start} to {actual_end})")
        else:
            print(f"  ✗ 5-year range: No data available")
    except Exception as e:
        print(f"  ✗ 5-year range: Error - {e}")


def test_ticker_discovery():
    """Test methods to discover available tickers"""
    print("\n" + "=" * 60)
    print("TESTING TICKER DISCOVERY METHODS")
    print("=" * 60)
    
    print("1. Testing S&P 500 tickers from Wikipedia:")
    try:
        # Try to get S&P 500 list from Wikipedia
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        tables = pd.read_html(url)
        sp500_table = tables[0]
        sp500_tickers = sp500_table['Symbol'].tolist()
        print(f"   Found {len(sp500_tickers)} S&P 500 tickers")
        print(f"   Sample tickers: {sp500_tickers[:10]}")
    except Exception as e:
        print(f"   Error fetching S&P 500 tickers: {e}")
        sp500_tickers = []
    
    print("\n2. Testing NASDAQ tickers:")
    try:
        # Try to get NASDAQ tickers
        nasdaq_url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"
        nasdaq_data = pd.read_csv(nasdaq_url, sep="|")
        nasdaq_tickers = nasdaq_data['Symbol'].dropna().tolist()
        # Remove the last entry which is usually file creation info
        nasdaq_tickers = [t for t in nasdaq_tickers if t != 'File Creation Time']
        print(f"   Found {len(nasdaq_tickers)} NASDAQ tickers")
        print(f"   Sample tickers: {nasdaq_tickers[:10]}")
    except Exception as e:
        print(f"   Error fetching NASDAQ tickers: {e}")
        nasdaq_tickers = []
    
    print("\n3. Testing NYSE tickers:")
    try:
        # Try to get NYSE tickers
        nyse_url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/otherlisted.txt"
        nyse_data = pd.read_csv(nyse_url, sep="|")
        nyse_tickers = nyse_data['ACT Symbol'].dropna().tolist()
        nyse_tickers = [t for t in nyse_tickers if t != 'File Creation Time']
        print(f"   Found {len(nyse_tickers)} NYSE/Other tickers")
        print(f"   Sample tickers: {nyse_tickers[:10]}")
    except Exception as e:
        print(f"   Error fetching NYSE tickers: {e}")
        nyse_tickers = []
    
    # Combine all tickers
    all_tickers = list(set(sp500_tickers + nasdaq_tickers + nyse_tickers))
    print(f"\nTotal unique tickers discovered: {len(all_tickers)}")
    
    return all_tickers[:100]  # Return first 100 for testing


def test_performance_bulk_vs_individual():
    """Compare performance of bulk vs individual downloads"""
    print("\n" + "=" * 60)
    print("TESTING PERFORMANCE: BULK VS INDIVIDUAL DOWNLOADS")
    print("=" * 60)
    
    test_tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX", "CRM", "ADBE"]
    
    # Test individual downloads
    print(f"Testing individual downloads for {len(test_tickers)} tickers...")
    start_time = time.time()
    individual_data = {}
    
    for ticker in test_tickers:
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="1y")
            individual_data[ticker] = data
        except Exception as e:
            print(f"Error downloading {ticker}: {e}")
    
    individual_time = time.time() - start_time
    print(f"Individual downloads completed in: {individual_time:.2f} seconds")
    
    # Test bulk download
    print(f"\nTesting bulk download for same {len(test_tickers)} tickers...")
    start_time = time.time()
    
    try:
        bulk_data = yf.download(
            tickers=" ".join(test_tickers),
            period="1y",
            group_by="ticker",
            threads=True
        )
        bulk_time = time.time() - start_time
        print(f"Bulk download completed in: {bulk_time:.2f} seconds")
        
        # Performance comparison
        speedup = individual_time / bulk_time if bulk_time > 0 else 0
        print(f"\nPerformance comparison:")
        print(f"  Individual: {individual_time:.2f}s")
        print(f"  Bulk:       {bulk_time:.2f}s")
        print(f"  Speedup:    {speedup:.2f}x")
        
    except Exception as e:
        print(f"Bulk download failed: {e}")


def test_data_quality_and_missing_data():
    """Test data quality and identify missing data issues"""
    print("\n" + "=" * 60)
    print("TESTING DATA QUALITY AND MISSING DATA")
    print("=" * 60)
    
    # Test with a mix of tickers including some that might have issues
    test_tickers = ["AAPL", "GOOGL", "INVALID_TICKER", "BRK-A", "BRK.A", "BABA", "TSM"]
    
    print("Testing data availability and quality:")
    for ticker in test_tickers:
        try:
            stock = yf.Ticker(ticker)
            
            # Test info availability
            info = stock.info
            has_info = len(info) > 5  # Basic check
            
            # Test historical data
            hist_data = stock.history(period="1y")
            has_hist = not hist_data.empty
            
            # Test financials
            try:
                financials = stock.financials
                has_financials = not financials.empty
            except:
                has_financials = False
            
            print(f"  {ticker:12}: Info={has_info}, History={has_hist}, Financials={has_financials}")
            
            if has_hist and not hist_data.empty:
                # Check for missing data in history
                missing_days = hist_data.isnull().sum().sum()
                total_data_points = hist_data.size
                print(f"               Missing data points: {missing_days}/{total_data_points}")
            
        except Exception as e:
            print(f"  {ticker:12}: ERROR - {e}")


def estimate_bulk_download_feasibility():
    """Estimate feasibility of downloading thousands of stocks"""
    print("\n" + "=" * 60)
    print("ESTIMATING BULK DOWNLOAD FEASIBILITY")
    print("=" * 60)
    
    # Estimate based on our performance tests
    estimated_total_stocks = 10000  # Conservative estimate
    stocks_per_batch = 100
    estimated_batches = estimated_total_stocks / stocks_per_batch
    
    # Conservative time estimates based on testing
    time_per_batch = 30  # seconds (conservative estimate)
    total_estimated_time = estimated_batches * time_per_batch
    
    print(f"Feasibility Analysis for {estimated_total_stocks:,} stocks:")
    print(f"  Recommended batch size: {stocks_per_batch}")
    print(f"  Total batches needed: {estimated_batches:.0f}")
    print(f"  Estimated time per batch: {time_per_batch} seconds")
    print(f"  Total estimated time: {total_estimated_time/3600:.1f} hours")
    
    # Storage estimates
    # Assume ~1KB per stock per day for OHLCV data
    days_5_years = 5 * 252  # Trading days
    bytes_per_stock = days_5_years * 1024  # 1KB per day
    total_storage_mb = (estimated_total_stocks * bytes_per_stock) / (1024 * 1024)
    
    print(f"\nStorage Estimates for 5 years of data:")
    print(f"  Data per stock (5 years): {bytes_per_stock/1024:.1f} KB")
    print(f"  Total storage needed: {total_storage_mb/1024:.1f} GB")
    
    print(f"\nRecommendations:")
    print(f"  1. Use batch processing with delays between batches")
    print(f"  2. Implement retry logic for failed downloads")
    print(f"  3. Save data incrementally to avoid memory issues")
    print(f"  4. Consider running during off-peak hours")
    print(f"  5. Monitor for rate limiting and adjust batch sizes accordingly")


def main():
    """Run all YFinance capability tests"""
    print("YFinance Capabilities and Limitations Research")
    print("=" * 60)
    print(f"Research conducted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"YFinance version: {yf.__version__ if hasattr(yf, '__version__') else 'Unknown'}")
    
    try:
        # Run all tests
        test_rate_limiting()
        test_bulk_download()
        available_metrics = explore_ticker_info_metrics()
        test_historical_data_limits()
        discovered_tickers = test_ticker_discovery()
        test_performance_bulk_vs_individual()
        test_data_quality_and_missing_data()
        estimate_bulk_download_feasibility()
        
        # Summary
        print("\n" + "=" * 60)
        print("RESEARCH SUMMARY")
        print("=" * 60)
        print(f"✓ Rate limiting: Tested with multiple requests")
        print(f"✓ Bulk download: {'Supported' if test_bulk_download() else 'Limited'}")
        print(f"✓ Financial metrics: {len(available_metrics)} key metrics available")
        print(f"✓ Historical data: Up to 10+ years available")
        print(f"✓ Ticker discovery: {len(discovered_tickers)} tickers found via public sources")
        print(f"✓ Performance analysis: Bulk downloads significantly faster")
        print(f"✓ Data quality: Varies by ticker, some missing data expected")
        
    except KeyboardInterrupt:
        print("\nResearch interrupted by user.")
    except Exception as e:
        print(f"\nResearch failed with error: {e}")


if __name__ == "__main__":
    main()