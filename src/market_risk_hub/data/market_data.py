"""
Market Data Fetcher - Retrieves financial data from Yahoo Finance
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import os
import pickle


class MarketDataFetcher:
    """
    Fetches and processes market data from Yahoo Finance.
    Includes caching functionality for efficient data retrieval.
    """

    def __init__(self, cache_dir: str = "data/cache"):
        """
        Initialize the Market Data Fetcher.

        Args:
            cache_dir: Directory for caching downloaded data
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def fetch_prices(
        self,
        tickers: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = "1y",
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Fetch historical price data for given tickers.

        Args:
            tickers: List of ticker symbols
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            period: Period to fetch if dates not specified (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            use_cache: Whether to use cached data

        Returns:
            DataFrame with adjusted close prices
        """
        cache_key = f"{'_'.join(sorted(tickers))}_{start_date}_{end_date}_{period}"
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")

        # Try to load from cache
        if use_cache and os.path.exists(cache_file):
            cache_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))
            if cache_age < timedelta(hours=24):  # Cache valid for 24 hours
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)

        # Fetch data from Yahoo Finance
        if start_date and end_date:
            data = yf.download(tickers, start=start_date, end=end_date, progress=False)
        else:
            data = yf.download(tickers, period=period, progress=False)

        # Extract adjusted close prices
        if len(tickers) == 1:
            prices = data['Adj Close'].to_frame()
            prices.columns = tickers
        else:
            prices = data['Adj Close']

        # Remove any rows with NaN values
        prices = prices.dropna()

        # Cache the data
        if use_cache:
            with open(cache_file, 'wb') as f:
                pickle.dump(prices, f)

        return prices

    def calculate_returns(
        self,
        prices: pd.DataFrame,
        method: str = "log"
    ) -> pd.DataFrame:
        """
        Calculate returns from price data.

        Args:
            prices: DataFrame of prices
            method: 'log' for log returns, 'simple' for simple returns

        Returns:
            DataFrame of returns
        """
        if method == "log":
            returns = np.log(prices / prices.shift(1))
        elif method == "simple":
            returns = prices.pct_change()
        else:
            raise ValueError("Method must be 'log' or 'simple'")

        return returns.dropna()

    def get_market_data(
        self,
        tickers: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = "1y",
        return_type: str = "log"
    ) -> Dict[str, pd.DataFrame]:
        """
        Convenience method to fetch prices and calculate returns.

        Args:
            tickers: List of ticker symbols
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            period: Period to fetch if dates not specified
            return_type: 'log' or 'simple'

        Returns:
            Dictionary with 'prices' and 'returns' DataFrames
        """
        prices = self.fetch_prices(tickers, start_date, end_date, period)
        returns = self.calculate_returns(prices, method=return_type)

        return {
            'prices': prices,
            'returns': returns
        }

    def get_risk_free_rate(self, period: str = "1y") -> float:
        """
        Fetch the risk-free rate using US Treasury yields (^TNX - 10 Year).

        Args:
            period: Period to average over

        Returns:
            Annualized risk-free rate as decimal
        """
        try:
            tnx = yf.download("^TNX", period=period, progress=False)['Adj Close']
            # TNX is in percentage, convert to decimal
            rf_rate = tnx.mean() / 100
            return rf_rate
        except:
            # Default to 4% if fetch fails
            return 0.04
