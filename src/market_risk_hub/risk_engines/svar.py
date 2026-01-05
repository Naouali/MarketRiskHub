"""
Stressed Value at Risk (SVaR) Calculator
Calculates VaR under stressed market conditions
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict, Union, Tuple
from datetime import datetime


class StressedVaR:
    """
    Calculate Stressed VaR by identifying historical stress periods
    and applying those scenarios to current portfolio.
    """

    def __init__(self, confidence_level: float = 0.95):
        """
        Initialize Stressed VaR Calculator.

        Args:
            confidence_level: Confidence level for SVaR calculation
        """
        self.confidence_level = confidence_level
        self.alpha = 1 - confidence_level

    def identify_stress_period(
        self,
        returns: pd.DataFrame,
        method: str = "volatility",
        percentile: float = 95
    ) -> Tuple[pd.Timestamp, pd.Timestamp]:
        """
        Identify historical stress periods based on various criteria.

        Args:
            returns: Historical returns DataFrame
            method: Method to identify stress ('volatility', 'drawdown', 'correlation')
            percentile: Percentile threshold for stress identification

        Returns:
            Tuple of (start_date, end_date) for stress period
        """
        if method == "volatility":
            # Find period with highest volatility
            rolling_vol = returns.std(axis=1).rolling(window=21).mean()
            threshold = np.percentile(rolling_vol.dropna(), percentile)
            stress_dates = rolling_vol[rolling_vol >= threshold].index

        elif method == "drawdown":
            # Find period with largest drawdown
            portfolio_returns = returns.mean(axis=1)
            cumulative = (1 + portfolio_returns).cumprod()
            running_max = cumulative.cummax()
            drawdown = (cumulative - running_max) / running_max
            threshold = np.percentile(drawdown, 100 - percentile)
            stress_dates = drawdown[drawdown <= threshold].index

        elif method == "correlation":
            # Find period when correlations increase (crisis periods)
            rolling_corr = returns.rolling(window=21).corr().groupby(level=0).mean().mean(axis=1)
            threshold = np.percentile(rolling_corr.dropna(), percentile)
            stress_dates = rolling_corr[rolling_corr >= threshold].index
        else:
            raise ValueError("Method must be 'volatility', 'drawdown', or 'correlation'")

        if len(stress_dates) == 0:
            raise ValueError("No stress period identified")

        return stress_dates[0], stress_dates[-1]

    def calculate_svar(
        self,
        returns: pd.DataFrame,
        portfolio_weights: Optional[np.ndarray] = None,
        stress_period: Optional[Tuple[str, str]] = None,
        method: str = "volatility"
    ) -> float:
        """
        Calculate Stressed VaR.

        Args:
            returns: Historical returns DataFrame
            portfolio_weights: Portfolio weights (equal weight if None)
            stress_period: Tuple of (start_date, end_date) for stress period
            method: Method to identify stress period if not provided

        Returns:
            Stressed VaR value
        """
        if portfolio_weights is None:
            portfolio_weights = np.array([1.0 / len(returns.columns)] * len(returns.columns))

        # Identify stress period if not provided
        if stress_period is None:
            start_date, end_date = self.identify_stress_period(returns, method=method)
        else:
            start_date, end_date = stress_period

        # Get returns during stress period
        stress_returns = returns.loc[start_date:end_date]

        # Calculate portfolio returns during stress
        portfolio_stress_returns = (stress_returns * portfolio_weights).sum(axis=1)

        # Calculate SVaR as percentile of stress period returns
        svar = -np.percentile(portfolio_stress_returns, self.alpha * 100)

        return svar

    def stress_test_scenarios(
        self,
        returns: pd.DataFrame,
        portfolio_weights: Optional[np.ndarray] = None
    ) -> Dict[str, float]:
        """
        Run multiple stress test scenarios.

        Args:
            returns: Historical returns DataFrame
            portfolio_weights: Portfolio weights

        Returns:
            Dictionary with SVaR for different scenarios
        """
        if portfolio_weights is None:
            portfolio_weights = np.array([1.0 / len(returns.columns)] * len(returns.columns))

        scenarios = {}

        # Standard stress scenarios
        try:
            scenarios['high_volatility'] = self.calculate_svar(
                returns, portfolio_weights, method='volatility'
            )
        except:
            scenarios['high_volatility'] = np.nan

        try:
            scenarios['max_drawdown'] = self.calculate_svar(
                returns, portfolio_weights, method='drawdown'
            )
        except:
            scenarios['max_drawdown'] = np.nan

        try:
            scenarios['high_correlation'] = self.calculate_svar(
                returns, portfolio_weights, method='correlation'
            )
        except:
            scenarios['high_correlation'] = np.nan

        # Historical crisis scenarios (if data available)
        crisis_periods = {
            '2008_financial_crisis': ('2008-09-01', '2009-03-31'),
            '2020_covid_crash': ('2020-02-15', '2020-04-15'),
            '2022_rate_hikes': ('2022-01-01', '2022-10-31')
        }

        for crisis_name, (start, end) in crisis_periods.items():
            try:
                if pd.Timestamp(start) >= returns.index[0] and pd.Timestamp(end) <= returns.index[-1]:
                    stress_returns = returns.loc[start:end]
                    portfolio_returns = (stress_returns * portfolio_weights).sum(axis=1)
                    scenarios[crisis_name] = -np.percentile(portfolio_returns, self.alpha * 100)
            except:
                continue

        return scenarios

    def marginal_svar(
        self,
        returns: pd.DataFrame,
        portfolio_weights: np.ndarray,
        stress_period: Optional[Tuple[str, str]] = None
    ) -> pd.Series:
        """
        Calculate marginal Stressed VaR (impact of small change in position).

        Args:
            returns: Historical returns DataFrame
            portfolio_weights: Portfolio weights
            stress_period: Stress period dates

        Returns:
            Series with marginal SVaR for each asset
        """
        base_svar = self.calculate_svar(returns, portfolio_weights, stress_period)

        marginal_svars = {}
        epsilon = 0.01

        for i, asset in enumerate(returns.columns):
            # Increase weight slightly
            perturbed_weights = portfolio_weights.copy()
            perturbed_weights[i] += epsilon
            perturbed_weights = perturbed_weights / perturbed_weights.sum()  # Renormalize

            perturbed_svar = self.calculate_svar(returns, perturbed_weights, stress_period)
            marginal_svars[asset] = (perturbed_svar - base_svar) / epsilon

        return pd.Series(marginal_svars, name='Marginal SVaR')
