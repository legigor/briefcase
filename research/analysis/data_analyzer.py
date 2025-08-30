#!/usr/bin/env python3
"""
Data Analysis Utility
Analyzes and reports on collected stock market data
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import numpy as np
from typing import Dict, List, Any


class DataAnalyzer:
    """Analyze collected stock data"""
    
    def __init__(self, data_dir: str = "./data/raw"):
        self.data_dir = Path(data_dir)
        self.historical_dir = self.data_dir / "historical"
        self.fundamentals_dir = self.data_dir / "fundamentals"
        self.metadata_dir = self.data_dir / "metadata"
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of collected data"""
        
        # Count files
        historical_files = list(self.historical_dir.glob("*.csv"))
        fundamental_files = list(self.fundamentals_dir.glob("*.json"))
        
        # Load collection summary if exists
        summary_file = self.metadata_dir / "collection_summary.json"
        if summary_file.exists():
            with open(summary_file, 'r') as f:
                collection_summary = json.load(f)
        else:
            collection_summary = {}
        
        # Calculate storage size
        total_size = 0
        for file in historical_files + fundamental_files:
            total_size += file.stat().st_size
        
        return {
            'historical_files': len(historical_files),
            'fundamental_files': len(fundamental_files),
            'total_tickers': len(historical_files),
            'total_size_mb': total_size / (1024 * 1024),
            'collection_summary': collection_summary
        }
    
    def analyze_ticker(self, ticker: str) -> Dict[str, Any]:
        """Analyze a specific ticker's data"""
        
        analysis = {'ticker': ticker}
        
        # Load historical data
        hist_file = self.historical_dir / f"{ticker}.csv"
        if hist_file.exists():
            df = pd.read_csv(hist_file, index_col='Date', parse_dates=True)
            
            analysis['historical'] = {
                'days_of_data': len(df),
                'start_date': df.index[0].strftime('%Y-%m-%d'),
                'end_date': df.index[-1].strftime('%Y-%m-%d'),
                'avg_daily_volume': df['Volume'].mean(),
                'price_range': {
                    'min': df['Low'].min(),
                    'max': df['High'].max(),
                    'current': df['Close'].iloc[-1]
                },
                'returns': {
                    '1_year': ((df['Close'].iloc[-1] / df['Close'].iloc[-252]) - 1) * 100 if len(df) > 252 else None,
                    '3_year': ((df['Close'].iloc[-1] / df['Close'].iloc[-756]) - 1) * 100 if len(df) > 756 else None,
                    '5_year': ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100 if len(df) > 1000 else None
                },
                'volatility': df['Close'].pct_change().std() * np.sqrt(252) * 100  # Annualized
            }
        
        # Load fundamental data
        fund_file = self.fundamentals_dir / f"{ticker}.json"
        if fund_file.exists():
            with open(fund_file, 'r') as f:
                fundamentals = json.load(f)
            
            analysis['fundamentals'] = {
                'market_cap': fundamentals.get('market_cap'),
                'pe_ratio': fundamentals.get('trailing_pe'),
                'dividend_yield': fundamentals.get('dividend_yield'),
                'sector': fundamentals.get('sector'),
                'industry': fundamentals.get('industry')
            }
        
        return analysis
    
    def get_sector_breakdown(self) -> Dict[str, int]:
        """Get breakdown of stocks by sector"""
        
        sectors = {}
        for fund_file in self.fundamentals_dir.glob("*.json"):
            with open(fund_file, 'r') as f:
                data = json.load(f)
                sector = data.get('sector', 'Unknown')
                sectors[sector] = sectors.get(sector, 0) + 1
        
        return dict(sorted(sectors.items(), key=lambda x: x[1], reverse=True))
    
    def get_top_performers(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get top performing stocks by 1-year return"""
        
        performers = []
        
        for hist_file in self.historical_dir.glob("*.csv"):
            ticker = hist_file.stem
            df = pd.read_csv(hist_file, index_col='Date', parse_dates=True)
            
            if len(df) > 252:  # At least 1 year of data
                one_year_return = ((df['Close'].iloc[-1] / df['Close'].iloc[-252]) - 1) * 100
                performers.append({
                    'ticker': ticker,
                    'return_1y': one_year_return,
                    'current_price': df['Close'].iloc[-1]
                })
        
        # Sort by return and get top N
        performers.sort(key=lambda x: x['return_1y'], reverse=True)
        return performers[:n]
    
    def generate_report(self):
        """Generate a comprehensive analysis report"""
        
        print("=" * 60)
        print("Stock Data Collection Analysis Report")
        print("=" * 60)
        print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Data summary
        summary = self.get_data_summary()
        print("Data Summary:")
        print(f"  - Historical data files: {summary['historical_files']}")
        print(f"  - Fundamental data files: {summary['fundamental_files']}")
        print(f"  - Total storage used: {summary['total_size_mb']:.2f} MB")
        
        if summary['collection_summary']:
            cs = summary['collection_summary']
            print(f"  - Collection date: {cs.get('collection_date', 'N/A')}")
            print(f"  - Successful tickers: {cs.get('successful', 0)}")
            print(f"  - Failed tickers: {cs.get('failed', 0)}")
            print(f"  - Data period: {cs.get('data_start_date', 'N/A')} to {cs.get('data_end_date', 'N/A')}")
        
        print()
        
        # Sector breakdown
        if summary['fundamental_files'] > 0:
            print("Sector Breakdown:")
            sectors = self.get_sector_breakdown()
            for sector, count in list(sectors.items())[:10]:
                print(f"  - {sector}: {count} stocks")
            print()
        
        # Top performers
        if summary['historical_files'] > 0:
            print("Top Performers (1-Year Return):")
            top_performers = self.get_top_performers(10)
            for i, performer in enumerate(top_performers, 1):
                print(f"  {i}. {performer['ticker']}: {performer['return_1y']:.2f}% "
                      f"(${performer['current_price']:.2f})")
        
        print("\n" + "=" * 60)
    
    def export_to_parquet(self):
        """Convert CSV files to Parquet format for better performance"""
        
        parquet_dir = self.data_dir.parent / "processed" / "parquet"
        parquet_dir.mkdir(parents=True, exist_ok=True)
        
        converted = 0
        for csv_file in self.historical_dir.glob("*.csv"):
            df = pd.read_csv(csv_file, index_col='Date', parse_dates=True)
            parquet_file = parquet_dir / f"{csv_file.stem}.parquet"
            df.to_parquet(parquet_file, compression='snappy')
            converted += 1
        
        print(f"Converted {converted} files to Parquet format in {parquet_dir}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze collected stock data")
    parser.add_argument('--ticker', type=str, help='Analyze specific ticker')
    parser.add_argument('--report', action='store_true', help='Generate full report')
    parser.add_argument('--export-parquet', action='store_true', 
                       help='Convert data to Parquet format')
    
    args = parser.parse_args()
    
    analyzer = DataAnalyzer()
    
    if args.ticker:
        # Analyze specific ticker
        analysis = analyzer.analyze_ticker(args.ticker.upper())
        print(json.dumps(analysis, indent=2, default=str))
    
    elif args.export_parquet:
        # Export to Parquet
        analyzer.export_to_parquet()
    
    else:
        # Generate report (default)
        analyzer.generate_report()


if __name__ == "__main__":
    main()