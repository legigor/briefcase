import yfinance as yf
import pandas as pd
import json

def main():
    ticker = yf.Ticker("AAPL")
    # print(json.dumps(ticker.info, indent=4))


    ticker_data = ticker.history(period="6mo")
    print(ticker_data.head())


if __name__ == "__main__":
    main()
