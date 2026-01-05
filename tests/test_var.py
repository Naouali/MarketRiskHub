"""
Unit tests for VaR calculations
"""

import unittest
import numpy as np
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from market_risk_hub.risk_engines.var import VaRCalculator


class TestVaRCalculator(unittest.TestCase):
    """Test cases for VaR Calculator"""

    def setUp(self):
        """Set up test data"""
        np.random.seed(42)

        # Generate synthetic returns
        n_obs = 1000
        self.returns_series = pd.Series(np.random.normal(0.001, 0.02, n_obs))

        # Multi-asset returns
        self.returns_df = pd.DataFrame({
            'Asset1': np.random.normal(0.001, 0.02, n_obs),
            'Asset2': np.random.normal(0.0008, 0.015, n_obs),
            'Asset3': np.random.normal(0.0012, 0.025, n_obs)
        })

        self.weights = np.array([0.4, 0.3, 0.3])
        self.var_calc = VaRCalculator(confidence_level=0.95)

    def test_historical_var_single_asset(self):
        """Test historical VaR for single asset"""
        var = self.var_calc.historical_var(self.returns_series)

        self.assertIsInstance(var, float)
        self.assertGreater(var, 0)  # VaR should be positive

    def test_historical_var_portfolio(self):
        """Test historical VaR for portfolio"""
        var = self.var_calc.historical_var(self.returns_df, self.weights)

        self.assertIsInstance(var, float)
        self.assertGreater(var, 0)

    def test_parametric_var(self):
        """Test parametric VaR"""
        var = self.var_calc.parametric_var(self.returns_df, self.weights, portfolio_value=100000)

        self.assertIsInstance(var, float)
        self.assertGreater(var, 0)

    def test_monte_carlo_var(self):
        """Test Monte Carlo VaR"""
        var = self.var_calc.monte_carlo_var(
            self.returns_df,
            self.weights,
            num_simulations=5000,
            random_seed=42
        )

        self.assertIsInstance(var, float)
        self.assertGreater(var, 0)

    def test_var_increases_with_confidence(self):
        """Test that VaR increases with confidence level"""
        var_95 = VaRCalculator(0.95).historical_var(self.returns_series)
        var_99 = VaRCalculator(0.99).historical_var(self.returns_series)

        self.assertGreater(var_99, var_95)

    def test_calculate_all(self):
        """Test calculate_all method"""
        results = self.var_calc.calculate_all(self.returns_df, self.weights)

        self.assertIn('historical_var', results)
        self.assertIn('parametric_var', results)
        self.assertIn('monte_carlo_var', results)

        for key, value in results.items():
            self.assertGreater(value, 0)

    def test_var_breakdown(self):
        """Test component VaR calculation"""
        component_var = self.var_calc.var_breakdown(self.returns_df, self.weights)

        self.assertIsInstance(component_var, pd.Series)
        self.assertEqual(len(component_var), len(self.weights))

    def test_weights_validation(self):
        """Test that weights are required for portfolio"""
        with self.assertRaises(ValueError):
            self.var_calc.historical_var(self.returns_df, portfolio_weights=None)


if __name__ == '__main__':
    unittest.main()
