"""
Expected Shortfall (ES) / Conditional Value at Risk (CVaR) Calculator
Measures the expected loss given that VaR threshold has been breached
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Optional, Union, Dict


class ExpectedShortfall:
    """
    Calculate Expected Shortfall (also known as Conditional VaR or CVaR).

    ES represents the expected loss given that the loss exceeds VaR threshold.
    It provides a more complete picture of tail risk than VaR alone.
    """

    def __init__(self, confidence_level: float = 0.95):
        """
        Initialize Expected Shortfall Calculator.

        Args:
            confidence_level: Confidence level for ES calculation
        """
        self.confidence_level = confidence_level
        self.alpha = 1 - confidence_level

    def historical_es(
        self,
        returns: Union[pd.Series, pd.DataFrame],
        portfolio_weights: Optional[np.ndarray] = None
    ) -> float:
        """
        Calculate Historical Expected Shortfall.

        Args:
            returns: Historical returns
            portfolio_weights: Portfolio weights (for DataFrame)

        Returns:
            Expected Shortfall value
        """
        if isinstance(returns, pd.DataFrame):
            if portfolio_weights is None:
                raise ValueError("Portfolio weights required for multiple assets")
            portfolio_returns = (returns * portfolio_weights).sum(axis=1)
        else:
            portfolio_returns = returns

        # Find VaR threshold
        var_threshold = np.percentile(portfolio_returns, self.alpha * 100)

        # Calculate average of losses beyond VaR
        tail_losses = portfolio_returns[portfolio_returns <= var_threshold]
        es = -tail_losses.mean()

        return es

    def parametric_es(
        self,
        returns: Union[pd.Series, pd.DataFrame],
        portfolio_weights: Optional[np.ndarray] = None,
        portfolio_value: float = 1.0
    ) -> float:
        """
        Calculate Parametric Expected Shortfall (assumes normal distribution).

        Args:
            returns: Historical returns
            portfolio_weights: Portfolio weights
            portfolio_value: Current portfolio value

        Returns:
            Expected Shortfall value
        """
        if isinstance(returns, pd.DataFrame):
            if portfolio_weights is None:
                raise ValueError("Portfolio weights required for multiple assets")

            mean_returns = returns.mean()
            cov_matrix = returns.cov()

            portfolio_mean = np.dot(portfolio_weights, mean_returns)
            portfolio_std = np.sqrt(np.dot(portfolio_weights.T, np.dot(cov_matrix, portfolio_weights)))
        else:
            portfolio_mean = returns.mean()
            portfolio_std = returns.std()

        # Calculate ES using normal distribution
        # ES = μ - σ * φ(Φ^(-1)(α)) / α
        # where φ is PDF and Φ is CDF of standard normal
        z_score = stats.norm.ppf(self.alpha)
        es = -(portfolio_mean - portfolio_std * stats.norm.pdf(z_score) / self.alpha) * portfolio_value

        return es

    def monte_carlo_es(
        self,
        returns: Union[pd.Series, pd.DataFrame],
        portfolio_weights: Optional[np.ndarray] = None,
        num_simulations: int = 10000,
        time_horizon: int = 1,
        random_seed: Optional[int] = None
    ) -> float:
        """
        Calculate Monte Carlo Expected Shortfall.

        Args:
            returns: Historical returns
            portfolio_weights: Portfolio weights
            num_simulations: Number of simulations
            time_horizon: Time horizon in days
            random_seed: Random seed for reproducibility

        Returns:
            Expected Shortfall value
        """
        if random_seed is not None:
            np.random.seed(random_seed)

        if isinstance(returns, pd.DataFrame):
            if portfolio_weights is None:
                raise ValueError("Portfolio weights required for multiple assets")

            mean_returns = returns.mean().values
            cov_matrix = returns.cov().values

            simulated_returns = np.random.multivariate_normal(
                mean_returns * time_horizon,
                cov_matrix * time_horizon,
                num_simulations
            )

            portfolio_returns = np.dot(simulated_returns, portfolio_weights)
        else:
            mean_return = returns.mean()
            std_return = returns.std()

            portfolio_returns = np.random.normal(
                mean_return * time_horizon,
                std_return * np.sqrt(time_horizon),
                num_simulations
            )

        # Calculate ES from simulated distribution
        var_threshold = np.percentile(portfolio_returns, self.alpha * 100)
        tail_losses = portfolio_returns[portfolio_returns <= var_threshold]
        es = -tail_losses.mean()

        return es

    def calculate_all(
        self,
        returns: Union[pd.Series, pd.DataFrame],
        portfolio_weights: Optional[np.ndarray] = None,
        portfolio_value: float = 1.0,
        num_simulations: int = 10000
    ) -> Dict[str, float]:
        """
        Calculate Expected Shortfall using all methods.

        Args:
            returns: Historical returns
            portfolio_weights: Portfolio weights
            portfolio_value: Current portfolio value
            num_simulations: Number of Monte Carlo simulations

        Returns:
            Dictionary with ES values from all methods
        """
        return {
            'historical_es': self.historical_es(returns, portfolio_weights),
            'parametric_es': self.parametric_es(returns, portfolio_weights, portfolio_value),
            'monte_carlo_es': self.monte_carlo_es(returns, portfolio_weights, num_simulations)
        }

    def es_ratio(
        self,
        returns: Union[pd.Series, pd.DataFrame],
        portfolio_weights: Optional[np.ndarray] = None,
        var: Optional[float] = None
    ) -> float:
        """
        Calculate ES/VaR ratio to measure tail risk severity.

        Higher ratio indicates fatter tails (more tail risk beyond VaR).

        Args:
            returns: Historical returns
            portfolio_weights: Portfolio weights
            var: Precomputed VaR (will calculate if None)

        Returns:
            ES/VaR ratio
        """
        es = self.historical_es(returns, portfolio_weights)

        if var is None:
            if isinstance(returns, pd.DataFrame):
                if portfolio_weights is None:
                    raise ValueError("Portfolio weights required")
                portfolio_returns = (returns * portfolio_weights).sum(axis=1)
            else:
                portfolio_returns = returns

            var = -np.percentile(portfolio_returns, self.alpha * 100)

        return es / var if var != 0 else np.nan

    def component_es(
        self,
        returns: pd.DataFrame,
        portfolio_weights: np.ndarray
    ) -> pd.Series:
        """
        Calculate component Expected Shortfall (risk contribution of each asset).

        Args:
            returns: Historical returns DataFrame
            portfolio_weights: Portfolio weights

        Returns:
            Series with component ES for each asset
        """
        # Calculate portfolio returns
        portfolio_returns = (returns * portfolio_weights).sum(axis=1)

        # Find VaR threshold
        var_threshold = np.percentile(portfolio_returns, self.alpha * 100)

        # Get tail scenarios
        tail_mask = portfolio_returns <= var_threshold
        tail_returns = returns[tail_mask]

        # Component ES = Weight * Average tail loss for each asset
        component_es = (tail_returns * portfolio_weights).mean()

        return pd.Series(component_es, name='Component ES')
