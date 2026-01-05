"""
Unit tests for VaR Backtesting
"""

import unittest
import numpy as np
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from market_risk_hub.backtesting.var_backtest import VaRBacktest


class TestVaRBacktest(unittest.TestCase):
    """Test cases for VaR Backtesting"""

    def setUp(self):
        """Set up test data"""
        np.random.seed(42)

        # Generate synthetic returns and VaR estimates
        n_obs = 250
        self.returns = pd.Series(np.random.normal(0, 0.02, n_obs))
        self.var_estimates = pd.Series(np.abs(np.random.normal(0.03, 0.005, n_obs)))

        self.backtest = VaRBacktest(confidence_level=0.95)

    def test_calculate_exceptions(self):
        """Test exception calculation"""
        exceptions = self.backtest.calculate_exceptions(self.returns, self.var_estimates)

        self.assertIsInstance(exceptions, pd.Series)
        self.assertEqual(len(exceptions), len(self.returns))
        self.assertTrue(all(exceptions.isin([0, 1])))

    def test_kupiec_pof_test(self):
        """Test Kupiec POF test"""
        result = self.backtest.kupiec_pof_test(self.returns, self.var_estimates)

        self.assertIn('test', result)
        self.assertIn('exceptions', result)
        self.assertIn('p_value', result)
        self.assertIn('reject_null', result)

        self.assertEqual(result['test'], 'Kupiec POF')
        self.assertIsInstance(result['reject_null'], bool)

    def test_christoffersen_test(self):
        """Test Christoffersen test"""
        result = self.backtest.christoffersen_test(self.returns, self.var_estimates)

        self.assertIn('test', result)
        self.assertIn('lr_cc_statistic', result)
        self.assertIn('p_value', result)

        self.assertEqual(result['test'], 'Christoffersen CC')

    def test_traffic_light_test(self):
        """Test traffic light test"""
        result = self.backtest.traffic_light_test(self.returns, self.var_estimates)

        self.assertIn('zone', result)
        self.assertIn('action', result)
        self.assertIn('exceptions', result)

        self.assertIn(result['zone'], ['GREEN', 'YELLOW', 'RED'])

    def test_comprehensive_backtest(self):
        """Test comprehensive backtest"""
        results = self.backtest.comprehensive_backtest(self.returns, self.var_estimates)

        self.assertIn('kupiec', results)
        self.assertIn('christoffersen', results)
        self.assertIn('traffic_light', results)

    def test_plot_backtest_results(self):
        """Test backtest results data preparation"""
        df = self.backtest.plot_backtest_results(self.returns, self.var_estimates)

        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn('returns', df.columns)
        self.assertIn('var', df.columns)
        self.assertIn('exceptions', df.columns)


if __name__ == '__main__':
    unittest.main()
