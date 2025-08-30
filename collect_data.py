#!/usr/bin/env python3
"""
Convenience script to run data collection
"""

from research.data_collection import StockDataCollector
import sys
import logging

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


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Stock Data Collection")
    parser.add_argument('--full', action='store_true',
                       help='Run full collection for all tickers')
    parser.add_argument('--test', action='store_true',
                       help='Test mode with 10 sample tickers')
    parser.add_argument('--tickers', nargs='+',
                       help='Specific tickers to download')
    parser.add_argument('--batch-size', type=int, default=100,
                       help='Batch size for downloads')
    parser.add_argument('--years', type=int, default=5,
                       help='Years of history to download')
    
    args = parser.parse_args()
    
    if args.full:
        logger.info("=" * 60)
        logger.info("Starting Full Stock Data Collection")
        logger.info("This will download 5 years of data for all stocks")
        logger.info("Estimated time: 1-2 hours")
        logger.info("=" * 60)
        
        response = input("\nProceed? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            logger.info("Cancelled")
            return
    
    collector = StockDataCollector(
        batch_size=args.batch_size,
        years_of_history=args.years
    )
    
    tickers = None
    if args.test:
        tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA',
                  'META', 'NVDA', 'NFLX', 'JPM', 'BAC']
        logger.info(f"Test mode: {len(tickers)} tickers")
    elif args.tickers:
        tickers = args.tickers
        logger.info(f"Downloading {len(tickers)} specified tickers")
    
    try:
        collector.collect_all_data(tickers=tickers, resume=True)
    except KeyboardInterrupt:
        logger.info("\nInterrupted. Progress saved.")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()