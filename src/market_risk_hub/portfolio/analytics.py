"""
Portfolio Analytics - Performance metrics, risk metrics, and portfolio optimization
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Dict, Optional, Tuple


class PortfolioAnalytics:
    """
    Comprehensive portfolio analytics including performance metrics,
    risk metrics, and optimization.
    """

    def __init__(self, returns: pd.DataFrame, weights: Optional[np.ndarray] = None):
        """
        Initialize Portfolio Analytics.

        Args:
            returns: DataFrame of asset returns
            weights: Portfolio weights (equal weight if None)
        """
        self.returns = returns
        self.n_assets = len(returns.columns)

        if weights is None:
            self.weights = np.array([1.0 / self.n_assets] * self.n_assets)
        else:
            self.weights = weights

        self.portfolio_returns = (returns * self.weights).sum(axis=1)

    def calculate_returns_metrics(self) -> Dict[str, float]:
        """
        Calculate portfolio return metrics.

        Returns:
            Dictionary with return metrics
        """
        portfolio_returns = self.portfolio_returns

        return {
            'mean_return': portfolio_returns.mean(),
            'annualized_return': portfolio_returns.mean() * 252,
            'cumulative_return': (1 + portfolio_returns).prod() - 1,
            'total_return': portfolio_returns.sum()
        }

    def calculate_risk_metrics(self, risk_free_rate: float = 0.02) -> Dict[str, float]:
        """
        Calculate portfolio risk metrics.

        Args:
            risk_free_rate: Annual risk-free rate

        Returns:
            Dictionary with risk metrics
        """
        portfolio_returns = self.portfolio_returns
        excess_returns = portfolio_returns - risk_free_rate / 252

        # Volatility
        volatility = portfolio_returns.std()
        annualized_volatility = volatility * np.sqrt(252)

        # Sharpe Ratio
        sharpe_ratio = (portfolio_returns.mean() - risk_free_rate / 252) / volatility * np.sqrt(252)

        # Sortino Ratio (downside deviation)
        downside_returns = portfolio_returns[portfolio_returns < 0]
        downside_std = downside_returns.std()
        sortino_ratio = (portfolio_returns.mean() - risk_free_rate / 252) / downside_std * np.sqrt(252)

        # Maximum Drawdown
        cumulative = (1 + portfolio_returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()

        # Calmar Ratio
        calmar_ratio = (portfolio_returns.mean() * 252) / abs(max_drawdown)

        return {
            'volatility': volatility,
            'annualized_volatility': annualized_volatility,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'calmar_ratio': calmar_ratio
        }

    def calculate_correlation_matrix(self) -> pd.DataFrame:
        """
        Calculate correlation matrix of asset returns.

        Returns:
            Correlation matrix DataFrame
        """
        return self.returns.corr()

    def calculate_covariance_matrix(self) -> pd.DataFrame:
        """
        Calculate covariance matrix of asset returns.

        Returns:
            Covariance matrix DataFrame
        """
        return self.returns.cov()

    def calculate_beta(self, market_returns: pd.Series) -> pd.Series:
        """
        Calculate beta for each asset relative to market.

        Args:
            market_returns: Market benchmark returns

        Returns:
            Series with beta for each asset
        """
        betas = {}
        for asset in self.returns.columns:
            covariance = self.returns[asset].cov(market_returns)
            market_variance = market_returns.var()
            betas[asset] = covariance / market_variance

        return pd.Series(betas, name='Beta')

    def efficient_frontier(
        self,
        n_portfolios: int = 100,
        risk_free_rate: float = 0.02
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate the efficient frontier.

        Args:
            n_portfolios: Number of portfolios to generate
            risk_free_rate: Annual risk-free rate

        Returns:
            Tuple of (returns, volatilities, sharpe_ratios)
        """
        mean_returns = self.returns.mean() * 252
        cov_matrix = self.returns.cov() * 252

        returns_range = np.linspace(mean_returns.min(), mean_returns.max(), n_portfolios)
        volatilities = []
        returns_list = []
        sharpe_ratios = []

        for target_return in returns_range:
            # Minimize volatility for target return
            constraints = [
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},  # Weights sum to 1
                {'type': 'eq', 'fun': lambda w: np.dot(w, mean_returns) - target_return}  # Target return
            ]
            bounds = tuple((0, 1) for _ in range(self.n_assets))
            initial_weights = np.array([1.0 / self.n_assets] * self.n_assets)

            result = minimize(
                lambda w: np.sqrt(np.dot(w.T, np.dot(cov_matrix, w))),
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )

            if result.success:
                volatility = np.sqrt(np.dot(result.x.T, np.dot(cov_matrix, result.x)))
                sharpe = (target_return - risk_free_rate) / volatility

                volatilities.append(volatility)
                returns_list.append(target_return)
                sharpe_ratios.append(sharpe)

        return np.array(returns_list), np.array(volatilities), np.array(sharpe_ratios)

    def optimize_sharpe_ratio(self, risk_free_rate: float = 0.02) -> Dict:
        """
        Find portfolio weights that maximize Sharpe ratio.

        Args:
            risk_free_rate: Annual risk-free rate

        Returns:
            Dictionary with optimal weights and metrics
        """
        mean_returns = self.returns.mean() * 252
        cov_matrix = self.returns.cov() * 252

        def negative_sharpe(weights):
            portfolio_return = np.dot(weights, mean_returns)
            portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            return -(portfolio_return - risk_free_rate) / portfolio_std

        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = tuple((0, 1) for _ in range(self.n_assets))
        initial_weights = np.array([1.0 / self.n_assets] * self.n_assets)

        result = minimize(
            negative_sharpe,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        optimal_weights = result.x
        optimal_return = np.dot(optimal_weights, mean_returns)
        optimal_volatility = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights)))
        optimal_sharpe = (optimal_return - risk_free_rate) / optimal_volatility

        return {
            'weights': pd.Series(optimal_weights, index=self.returns.columns),
            'return': optimal_return,
            'volatility': optimal_volatility,
            'sharpe_ratio': optimal_sharpe
        }

    def optimize_minimum_variance(self) -> Dict:
        """
        Find minimum variance portfolio.

        Returns:
            Dictionary with optimal weights and metrics
        """
        mean_returns = self.returns.mean() * 252
        cov_matrix = self.returns.cov() * 252

        def portfolio_variance(weights):
            return np.dot(weights.T, np.dot(cov_matrix, weights))

        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = tuple((0, 1) for _ in range(self.n_assets))
        initial_weights = np.array([1.0 / self.n_assets] * self.n_assets)

        result = minimize(
            portfolio_variance,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        optimal_weights = result.x
        optimal_return = np.dot(optimal_weights, mean_returns)
        optimal_volatility = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights)))

        return {
            'weights': pd.Series(optimal_weights, index=self.returns.columns),
            'return': optimal_return,
            'volatility': optimal_volatility
        }

    def get_summary(self, risk_free_rate: float = 0.02) -> pd.DataFrame:
        """
        Get comprehensive portfolio summary.

        Args:
            risk_free_rate: Annual risk-free rate

        Returns:
            DataFrame with all portfolio metrics
        """
        returns_metrics = self.calculate_returns_metrics()
        risk_metrics = self.calculate_risk_metrics(risk_free_rate)

        summary = {**returns_metrics, **risk_metrics}

        return pd.Series(summary, name='Portfolio Metrics')
