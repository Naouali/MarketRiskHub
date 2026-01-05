"""
Unit tests for Portfolio Analytics
"""

import unittest
import numpy as np
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from market_risk_hub.portfolio.analytics import PortfolioAnalytics


class TestPortfolioAnalytics(unittest.TestCase):
    """Test cases for Portfolio Analytics"""

    def setUp(self):
        """Set up test data"""
        np.random.seed(42)

        # Generate synthetic returns
        n_obs = 1000
        self.returns = pd.DataFrame({
            'Asset1': np.random.normal(0.001, 0.02, n_obs),
            'Asset2': np.random.normal(0.0008, 0.015, n_obs),
            'Asset3': np.random.normal(0.0012, 0.025, n_obs)
        })

        self.weights = np.array([0.4, 0.3, 0.3])
        self.portfolio = PortfolioAnalytics(self.returns, self.weights)

    def test_initialization(self):
        """Test portfolio initialization"""
        self.assertEqual(self.portfolio.n_assets, 3)
        np.testing.assert_array_equal(self.portfolio.weights, self.weights)

    def test_equal_weights_default(self):
        """Test that equal weights are used by default"""
        portfolio = PortfolioAnalytics(self.returns)
        expected_weights = np.array([1/3, 1/3, 1/3])
        np.testing.assert_array_almost_equal(portfolio.weights, expected_weights)

    def test_calculate_returns_metrics(self):
        """Test return metrics calculation"""
        metrics = self.portfolio.calculate_returns_metrics()

        self.assertIn('mean_return', metrics)
        self.assertIn('annualized_return', metrics)
        self.assertIn('cumulative_return', metrics)

    def test_calculate_risk_metrics(self):
        """Test risk metrics calculation"""
        metrics = self.portfolio.calculate_risk_metrics(risk_free_rate=0.02)

        self.assertIn('volatility', metrics)
        self.assertIn('sharpe_ratio', metrics)
        self.assertIn('max_drawdown', metrics)

        self.assertGreater(metrics['volatility'], 0)
        self.assertLess(metrics['max_drawdown'], 0)  # Drawdown is negative

    def test_correlation_matrix(self):
        """Test correlation matrix calculation"""
        corr = self.portfolio.calculate_correlation_matrix()

        self.assertIsInstance(corr, pd.DataFrame)
        self.assertEqual(corr.shape, (3, 3))

        # Diagonal should be 1
        np.testing.assert_array_almost_equal(np.diag(corr), [1, 1, 1])

    def test_covariance_matrix(self):
        """Test covariance matrix calculation"""
        cov = self.portfolio.calculate_covariance_matrix()

        self.assertIsInstance(cov, pd.DataFrame)
        self.assertEqual(cov.shape, (3, 3))

    def test_optimize_sharpe_ratio(self):
        """Test Sharpe ratio optimization"""
        result = self.portfolio.optimize_sharpe_ratio(risk_free_rate=0.02)

        self.assertIn('weights', result)
        self.assertIn('return', result)
        self.assertIn('volatility', result)
        self.assertIn('sharpe_ratio', result)

        # Weights should sum to 1
        self.assertAlmostEqual(result['weights'].sum(), 1.0, places=5)

        # All weights should be non-negative
        self.assertTrue(all(result['weights'] >= -1e-6))

    def test_optimize_minimum_variance(self):
        """Test minimum variance optimization"""
        result = self.portfolio.optimize_minimum_variance()

        self.assertIn('weights', result)
        self.assertIn('volatility', result)

        # Weights should sum to 1
        self.assertAlmostEqual(result['weights'].sum(), 1.0, places=5)

    def test_efficient_frontier(self):
        """Test efficient frontier calculation"""
        returns, vols, sharpes = self.portfolio.efficient_frontier(n_portfolios=10)

        self.assertEqual(len(returns), len(vols))
        self.assertEqual(len(returns), len(sharpes))
        self.assertTrue(all(vols > 0))

    def test_get_summary(self):
        """Test comprehensive portfolio summary"""
        summary = self.portfolio.get_summary(risk_free_rate=0.02)

        self.assertIsInstance(summary, pd.Series)
        self.assertGreater(len(summary), 0)


if __name__ == '__main__':
    unittest.main()
