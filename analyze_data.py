#!/usr/bin/env python3
"""
Convenience script to analyze collected data
"""

from research.analysis import DataAnalyzer
import json


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze collected stock data")
    parser.add_argument('--ticker', type=str, help='Analyze specific ticker')
    parser.add_argument('--report', action='store_true', help='Generate full report')
    parser.add_argument('--export-parquet', action='store_true', 
                       help='Convert data to Parquet format')
    parser.add_argument('--top-performers', type=int, 
                       help='Show top N performers')
    parser.add_argument('--sectors', action='store_true',
                       help='Show sector breakdown')
    
    args = parser.parse_args()
    
    analyzer = DataAnalyzer()
    
    if args.ticker:
        # Analyze specific ticker
        analysis = analyzer.analyze_ticker(args.ticker.upper())
        print(json.dumps(analysis, indent=2, default=str))
    
    elif args.export_parquet:
        # Export to Parquet
        analyzer.export_to_parquet()
    
    elif args.top_performers:
        # Show top performers
        performers = analyzer.get_top_performers(args.top_performers)
        print(f"\nTop {args.top_performers} Performers (1-Year Return):")
        for i, p in enumerate(performers, 1):
            print(f"{i:3}. {p['ticker']:6} {p['return_1y']:+7.2f}% (${p['current_price']:.2f})")
    
    elif args.sectors:
        # Show sector breakdown
        sectors = analyzer.get_sector_breakdown()
        print("\nSector Breakdown:")
        for sector, count in sectors.items():
            print(f"  {sector:30} {count:5} stocks")
    
    else:
        # Generate report (default)
        analyzer.generate_report()


if __name__ == "__main__":
    main()