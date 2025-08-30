#!/usr/bin/env python3
"""
Full Stock Data Collection Script
Downloads historical data and fundamentals for all available stocks
"""

import sys
import logging
from .stock_data_collector import StockDataCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('full_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Run full stock data collection"""
    
    logger.info("=" * 60)
    logger.info("Starting Full Stock Data Collection")
    logger.info("=" * 60)
    logger.info("This will download 5 years of historical data for all available stocks")
    logger.info("Estimated time: 1-2 hours")
    logger.info("Estimated storage: 12-15 GB")
    logger.info("=" * 60)
    
    # Ask for confirmation
    response = input("\nDo you want to proceed with full collection? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        logger.info("Collection cancelled by user")
        return
    
    # Initialize collector with optimized settings
    collector = StockDataCollector(
        data_dir="./data/raw",
        batch_size=100,  # Optimal batch size based on testing
        years_of_history=5,  # 5 years as requested
        delay_between_batches=2.0  # Small delay to be respectful
    )
    
    try:
        # Run full collection (will automatically fetch all tickers)
        collector.collect_all_data(
            tickers=None,  # None means fetch all available
            resume=True    # Allow resuming if interrupted
        )
        
        logger.info("Full collection completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("\nCollection interrupted by user. Progress saved.")
        logger.info("Run this script again to resume from where you left off.")
        
    except Exception as e:
        logger.error(f"Collection failed with error: {e}")
        logger.info("Progress has been saved. You can resume by running this script again.")
        sys.exit(1)


if __name__ == "__main__":
    main()