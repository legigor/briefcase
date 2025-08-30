#!/usr/bin/env python3
"""
Stock Data Collector - Downloads historical data and financial metrics for all available stocks
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json
import time
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging
import pickle
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings

# Suppress yfinance warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class StockDataCollector:
    """Main class for collecting stock market data"""
    
    def __init__(self, data_dir: str = "./data/raw", batch_size: int = 100, 
                 years_of_history: int = 5, delay_between_batches: float = 2.0):
        """
        Initialize the data collector
        
        Args:
            data_dir: Directory to store collected data
            batch_size: Number of tickers to download in each batch
            years_of_history: Number of years of historical data to collect
            delay_between_batches: Delay in seconds between batch downloads
        """
        self.data_dir = Path(data_dir)
        self.batch_size = batch_size
        self.years_of_history = years_of_history
        self.delay_between_batches = delay_between_batches
        
        # Create directory structure
        self.historical_dir = self.data_dir / "historical"
        self.fundamentals_dir = self.data_dir / "fundamentals"
        self.metadata_dir = self.data_dir / "metadata"
        
        for dir_path in [self.historical_dir, self.fundamentals_dir, self.metadata_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Track progress
        self.failed_tickers = []
        self.successful_tickers = []
        self.progress_file = self.metadata_dir / "collection_progress.json"
        
    def get_all_tickers(self) -> List[str]:
        """
        Fetch all available stock tickers from NASDAQ and NYSE
        
        Returns:
            List of unique ticker symbols
        """
        logger.info("Fetching ticker lists from exchanges...")
        all_tickers = []
        
        # Fetch NASDAQ tickers
        try:
            nasdaq_url = "https://raw.githubusercontent.com/datasets/nasdaq-listings/master/data/nasdaq-listed.csv"
            nasdaq_data = pd.read_csv(nasdaq_url)
            # Convert to string and drop NaN values
            nasdaq_tickers = nasdaq_data['Symbol'].dropna().astype(str).tolist()
            logger.info(f"Found {len(nasdaq_tickers)} NASDAQ tickers")
            all_tickers.extend(nasdaq_tickers)
        except Exception as e:
            logger.error(f"Failed to fetch NASDAQ tickers: {e}")
            # Fallback to FTP if GitHub fails
            try:
                nasdaq_url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"
                nasdaq_data = pd.read_csv(nasdaq_url, sep="|")
                nasdaq_tickers = nasdaq_data['Symbol'].dropna().astype(str).tolist()
                nasdaq_tickers = [t for t in nasdaq_tickers if t != 'File Creation Time']
                logger.info(f"Found {len(nasdaq_tickers)} NASDAQ tickers (FTP)")
                all_tickers.extend(nasdaq_tickers)
            except Exception as e2:
                logger.error(f"Failed to fetch NASDAQ tickers from FTP: {e2}")
        
        # Fetch NYSE and other exchange tickers
        try:
            nyse_url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/otherlisted.txt"
            nyse_data = pd.read_csv(nyse_url, sep="|")
            nyse_tickers = nyse_data['ACT Symbol'].dropna().astype(str).tolist()
            nyse_tickers = [t for t in nyse_tickers if t != 'File Creation Time']
            logger.info(f"Found {len(nyse_tickers)} NYSE/Other tickers")
            all_tickers.extend(nyse_tickers)
        except Exception as e:
            logger.error(f"Failed to fetch NYSE tickers: {e}")
        
        # Remove duplicates and clean
        all_tickers = list(set(all_tickers))
        # Remove tickers with special characters that might cause issues
        # Also handle cases where ticker might be float (NaN) or other non-string types
        cleaned_tickers = []
        for t in all_tickers:
            if t and isinstance(t, str) and not any(c in t for c in ['$', '^', '~']):
                cleaned_tickers.append(t)
        all_tickers = cleaned_tickers
        
        logger.info(f"Total unique tickers found: {len(all_tickers)}")
        
        # Save ticker list
        ticker_file = self.metadata_dir / "all_tickers.json"
        with open(ticker_file, 'w') as f:
            json.dump(sorted(all_tickers), f, indent=2)
        logger.info(f"Saved ticker list to {ticker_file}")
        
        return sorted(all_tickers)
    
    def download_batch_historical(self, tickers: List[str], 
                                start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
        """
        Download historical data for a batch of tickers
        
        Args:
            tickers: List of ticker symbols
            start_date: Start date for historical data
            end_date: End date for historical data
            
        Returns:
            Dictionary mapping ticker to DataFrame of historical data
        """
        try:
            # Use yfinance bulk download
            data = yf.download(
                tickers=" ".join(tickers),
                start=start_date,
                end=end_date,
                group_by='ticker',
                threads=True,
                progress=False
            )
            
            # Parse the multi-level column DataFrame
            result = {}
            if len(tickers) == 1:
                # Single ticker returns simple DataFrame
                if not data.empty:
                    result[tickers[0]] = data
            else:
                # Multiple tickers return multi-level columns
                for ticker in tickers:
                    try:
                        if ticker in data.columns.levels[0]:
                            ticker_data = data[ticker].dropna()
                            if not ticker_data.empty:
                                result[ticker] = ticker_data
                    except:
                        # Try alternative structure
                        try:
                            ticker_data = data.xs(ticker, level='Ticker', axis=1)
                            if not ticker_data.empty:
                                result[ticker] = ticker_data
                        except:
                            pass
            
            return result
            
        except Exception as e:
            logger.error(f"Error downloading batch: {e}")
            return {}
    
    def download_fundamentals(self, ticker: str) -> Dict[str, Any]:
        """
        Download fundamental data and financial metrics for a ticker
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary of fundamental data
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Extract key metrics
            fundamentals = {
                'ticker': ticker,
                'timestamp': datetime.now().isoformat(),
                'market_cap': info.get('marketCap'),
                'enterprise_value': info.get('enterpriseValue'),
                'trailing_pe': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'price_to_book': info.get('priceToBook'),
                'price_to_sales': info.get('priceToSalesTrailing12Months'),
                'enterprise_to_revenue': info.get('enterpriseToRevenue'),
                'enterprise_to_ebitda': info.get('enterpriseToEbitda'),
                'profit_margins': info.get('profitMargins'),
                'operating_margins': info.get('operatingMargins'),
                'return_on_assets': info.get('returnOnAssets'),
                'return_on_equity': info.get('returnOnEquity'),
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),
                'current_ratio': info.get('currentRatio'),
                'quick_ratio': info.get('quickRatio'),
                'debt_to_equity': info.get('debtToEquity'),
                'free_cashflow': info.get('freeCashflow'),
                'dividend_yield': info.get('dividendYield'),
                'payout_ratio': info.get('payoutRatio'),
                'beta': info.get('beta'),
                'shares_outstanding': info.get('sharesOutstanding'),
                'float_shares': info.get('floatShares'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'country': info.get('country'),
                'website': info.get('website'),
                'description': info.get('longBusinessSummary')
            }
            
            return fundamentals
            
        except Exception as e:
            logger.debug(f"Error fetching fundamentals for {ticker}: {e}")
            return {}
    
    def save_historical_data(self, ticker: str, data: pd.DataFrame):
        """Save historical data to CSV file"""
        if data.empty:
            return
        
        filename = self.historical_dir / f"{ticker}.csv"
        data.to_csv(filename)
        logger.debug(f"Saved historical data for {ticker}")
    
    def save_fundamentals(self, fundamentals: Dict[str, Any]):
        """Save fundamental data to JSON file"""
        if not fundamentals or 'ticker' not in fundamentals:
            return
        
        ticker = fundamentals['ticker']
        filename = self.fundamentals_dir / f"{ticker}.json"
        with open(filename, 'w') as f:
            json.dump(fundamentals, f, indent=2, default=str)
        logger.debug(f"Saved fundamentals for {ticker}")
    
    def load_progress(self) -> Dict[str, Any]:
        """Load collection progress from file"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {
            'successful_tickers': [],
            'failed_tickers': [],
            'last_batch_index': 0
        }
    
    def save_progress(self, batch_index: int):
        """Save collection progress to file"""
        progress = {
            'successful_tickers': self.successful_tickers,
            'failed_tickers': self.failed_tickers,
            'last_batch_index': batch_index,
            'timestamp': datetime.now().isoformat()
        }
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
    
    def collect_all_data(self, tickers: Optional[List[str]] = None, resume: bool = True):
        """
        Main method to collect all stock data
        
        Args:
            tickers: Optional list of tickers to download. If None, fetches all available.
            resume: Whether to resume from previous progress
        """
        # Get tickers
        if tickers is None:
            tickers = self.get_all_tickers()
        
        # Load progress if resuming
        start_batch = 0
        if resume:
            progress = self.load_progress()
            self.successful_tickers = progress.get('successful_tickers', [])
            self.failed_tickers = progress.get('failed_tickers', [])
            start_batch = progress.get('last_batch_index', 0)
            
            # Filter out already processed tickers
            processed = set(self.successful_tickers + self.failed_tickers)
            tickers = [t for t in tickers if t not in processed]
            
            if start_batch > 0:
                logger.info(f"Resuming from batch {start_batch}, {len(processed)} tickers already processed")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.years_of_history * 365)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        logger.info(f"Collecting data from {start_date_str} to {end_date_str}")
        logger.info(f"Total tickers to process: {len(tickers)}")
        
        # Process in batches
        total_batches = (len(tickers) + self.batch_size - 1) // self.batch_size
        
        for batch_idx in range(start_batch, total_batches):
            batch_start = batch_idx * self.batch_size
            batch_end = min(batch_start + self.batch_size, len(tickers))
            batch_tickers = tickers[batch_start:batch_end]
            
            logger.info(f"Processing batch {batch_idx + 1}/{total_batches} ({len(batch_tickers)} tickers)")
            
            # Download historical data for batch
            historical_data = self.download_batch_historical(
                batch_tickers, start_date_str, end_date_str
            )
            
            # Process each ticker in the batch
            batch_successful = 0
            batch_failed = 0
            
            for ticker in batch_tickers:
                try:
                    # Save historical data if available
                    if ticker in historical_data:
                        self.save_historical_data(ticker, historical_data[ticker])
                        
                        # Download and save fundamentals
                        fundamentals = self.download_fundamentals(ticker)
                        if fundamentals:
                            self.save_fundamentals(fundamentals)
                        
                        self.successful_tickers.append(ticker)
                        batch_successful += 1
                    else:
                        self.failed_tickers.append(ticker)
                        batch_failed += 1
                        logger.debug(f"No data available for {ticker}")
                        
                except Exception as e:
                    self.failed_tickers.append(ticker)
                    batch_failed += 1
                    logger.error(f"Error processing {ticker}: {e}")
            
            logger.info(f"Batch complete: {batch_successful} successful, {batch_failed} failed")
            
            # Save progress
            self.save_progress(batch_idx + 1)
            
            # Delay between batches to avoid rate limiting
            if batch_idx < total_batches - 1:
                time.sleep(self.delay_between_batches)
        
        # Final summary
        logger.info("=" * 60)
        logger.info("Data collection complete!")
        logger.info(f"Successfully collected: {len(self.successful_tickers)} tickers")
        logger.info(f"Failed: {len(self.failed_tickers)} tickers")
        
        # Save final summary
        summary = {
            'total_tickers': len(self.successful_tickers) + len(self.failed_tickers),
            'successful': len(self.successful_tickers),
            'failed': len(self.failed_tickers),
            'successful_tickers': sorted(self.successful_tickers),
            'failed_tickers': sorted(self.failed_tickers),
            'collection_date': datetime.now().isoformat(),
            'years_of_history': self.years_of_history,
            'data_start_date': start_date_str,
            'data_end_date': end_date_str
        }
        
        summary_file = self.metadata_dir / "collection_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Summary saved to {summary_file}")


def main():
    """Main entry point for the data collector"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Stock Data Collector")
    parser.add_argument('--batch-size', type=int, default=100,
                       help='Number of tickers per batch (default: 100)')
    parser.add_argument('--years', type=int, default=5,
                       help='Years of historical data to collect (default: 5)')
    parser.add_argument('--delay', type=float, default=2.0,
                       help='Delay between batches in seconds (default: 2.0)')
    parser.add_argument('--no-resume', action='store_true',
                       help='Start fresh instead of resuming previous collection')
    parser.add_argument('--tickers', nargs='+',
                       help='Specific tickers to download (default: all available)')
    parser.add_argument('--test', action='store_true',
                       help='Test mode: download only first 10 tickers')
    
    args = parser.parse_args()
    
    # Initialize collector
    collector = StockDataCollector(
        batch_size=args.batch_size,
        years_of_history=args.years,
        delay_between_batches=args.delay
    )
    
    # Determine tickers to download
    tickers = args.tickers
    if args.test:
        # Test mode: use a small set of popular tickers
        tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 
                  'META', 'NVDA', 'NFLX', 'JPM', 'BAC']
        logger.info("Running in test mode with 10 tickers")
    
    # Run collection
    collector.collect_all_data(
        tickers=tickers,
        resume=not args.no_resume
    )


if __name__ == "__main__":
    main()