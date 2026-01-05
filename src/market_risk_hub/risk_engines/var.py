"""
Value at Risk (VaR) Calculator
Supports multiple methodologies: Historical, Parametric (Variance-Covariance), and Monte Carlo
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Optional, Dict, Union


class VaRCalculator:
    """
    Calculate Value at Risk using various methodologies.

    VaR represents the maximum potential loss over a given time horizon
    at a specified confidence level.
    """

    def __init__(self, confidence_level: float = 0.95):
        """
        Initialize VaR Calculator.

        Args:
            confidence_level: Confidence level for VaR calculation (default 0.95 for 95%)
        """
        self.confidence_level = confidence_level
        self.alpha = 1 - confidence_level

    def historical_var(
        self,
        returns: Union[pd.Series, pd.DataFrame],
        portfolio_weights: Optional[np.ndarray] = None
    ) -> float:
        """
        Calculate Historical VaR using empirical distribution of returns.

        Args:
            returns: Historical returns (Series for single asset, DataFrame for portfolio)
            portfolio_weights: Weights for portfolio (required if returns is DataFrame)

        Returns:
            VaR value (as positive number representing potential loss)
        """
        if isinstance(returns, pd.DataFrame):
            if portfolio_weights is None:
                raise ValueError("Portfolio weights required for multiple assets")
            portfolio_returns = (returns * portfolio_weights).sum(axis=1)
        else:
            portfolio_returns = returns

        # Calculate VaR as the alpha quantile
        var = -np.percentile(portfolio_returns, self.alpha * 100)
        return var

    def parametric_var(
        self,
        returns: Union[pd.Series, pd.DataFrame],
        portfolio_weights: Optional[np.ndarray] = None,
        portfolio_value: float = 1.0
    ) -> float:
        """
        Calculate Parametric VaR (Variance-Covariance method).
        Assumes returns are normally distributed.

        Args:
            returns: Historical returns
            portfolio_weights: Weights for portfolio (required if returns is DataFrame)
            portfolio_value: Current portfolio value (default 1.0)

        Returns:
            VaR value
        """
        if isinstance(returns, pd.DataFrame):
            if portfolio_weights is None:
                raise ValueError("Portfolio weights required for multiple assets")

            # Calculate portfolio mean and standard deviation
            mean_returns = returns.mean()
            cov_matrix = returns.cov()

            portfolio_mean = np.dot(portfolio_weights, mean_returns)
            portfolio_std = np.sqrt(np.dot(portfolio_weights.T, np.dot(cov_matrix, portfolio_weights)))
        else:
            portfolio_mean = returns.mean()
            portfolio_std = returns.std()

        # Calculate VaR using normal distribution
        z_score = stats.norm.ppf(self.alpha)
        var = -(portfolio_mean + z_score * portfolio_std) * portfolio_value

        return var

    def monte_carlo_var(
        self,
        returns: Union[pd.Series, pd.DataFrame],
        portfolio_weights: Optional[np.ndarray] = None,
        num_simulations: int = 10000,
        time_horizon: int = 1,
        random_seed: Optional[int] = None
    ) -> float:
        """
        Calculate Monte Carlo VaR by simulating future returns.

        Args:
            returns: Historical returns
            portfolio_weights: Weights for portfolio (required if returns is DataFrame)
            num_simulations: Number of Monte Carlo simulations
            time_horizon: Time horizon in days
            random_seed: Random seed for reproducibility

        Returns:
            VaR value
        """
        if random_seed is not None:
            np.random.seed(random_seed)

        if isinstance(returns, pd.DataFrame):
            if portfolio_weights is None:
                raise ValueError("Portfolio weights required for multiple assets")

            mean_returns = returns.mean().values
            cov_matrix = returns.cov().values

            # Generate correlated random returns
            simulated_returns = np.random.multivariate_normal(
                mean_returns * time_horizon,
                cov_matrix * time_horizon,
                num_simulations
            )

            # Calculate portfolio returns
            portfolio_returns = np.dot(simulated_returns, portfolio_weights)
        else:
            mean_return = returns.mean()
            std_return = returns.std()

            # Generate random returns
            portfolio_returns = np.random.normal(
                mean_return * time_horizon,
                std_return * np.sqrt(time_horizon),
                num_simulations
            )

        # Calculate VaR from simulated distribution
        var = -np.percentile(portfolio_returns, self.alpha * 100)
        return var

    def calculate_all(
        self,
        returns: Union[pd.Series, pd.DataFrame],
        portfolio_weights: Optional[np.ndarray] = None,
        portfolio_value: float = 1.0,
        num_simulations: int = 10000
    ) -> Dict[str, float]:
        """
        Calculate VaR using all three methods.

        Args:
            returns: Historical returns
            portfolio_weights: Weights for portfolio
            portfolio_value: Current portfolio value
            num_simulations: Number of Monte Carlo simulations

        Returns:
            Dictionary with VaR values from all methods
        """
        return {
            'historical_var': self.historical_var(returns, portfolio_weights),
            'parametric_var': self.parametric_var(returns, portfolio_weights, portfolio_value),
            'monte_carlo_var': self.monte_carlo_var(returns, portfolio_weights, num_simulations)
        }

    def var_breakdown(
        self,
        returns: pd.DataFrame,
        portfolio_weights: np.ndarray
    ) -> pd.Series:
        """
        Calculate component VaR (risk contribution of each asset).

        Args:
            returns: Historical returns DataFrame
            portfolio_weights: Portfolio weights

        Returns:
            Series with component VaR for each asset
        """
        # Calculate portfolio statistics
        mean_returns = returns.mean().values
        cov_matrix = returns.cov().values

        portfolio_variance = np.dot(portfolio_weights.T, np.dot(cov_matrix, portfolio_weights))
        portfolio_std = np.sqrt(portfolio_variance)

        # Marginal VaR = (Covariance with portfolio) / Portfolio Std
        marginal_var = np.dot(cov_matrix, portfolio_weights) / portfolio_std

        # Component VaR = Weight * Marginal VaR
        component_var = portfolio_weights * marginal_var

        return pd.Series(component_var, index=returns.columns, name='Component VaR')
