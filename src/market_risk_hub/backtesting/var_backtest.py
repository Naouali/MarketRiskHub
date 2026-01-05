"""
VaR Backtesting - Validate VaR model accuracy
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Tuple, Union


class VaRBacktest:
    """
    Backtest VaR models to validate their accuracy.

    Implements standard backtesting procedures including:
    - Kupiec POF Test (Unconditional Coverage)
    - Christoffersen Test (Conditional Coverage)
    - Traffic Light Approach (Basel)
    """

    def __init__(self, confidence_level: float = 0.95):
        """
        Initialize VaR Backtesting.

        Args:
            confidence_level: VaR confidence level
        """
        self.confidence_level = confidence_level
        self.alpha = 1 - confidence_level

    def calculate_exceptions(
        self,
        actual_returns: pd.Series,
        var_estimates: pd.Series
    ) -> pd.Series:
        """
        Calculate VaR exceptions (breaches).

        Args:
            actual_returns: Actual portfolio returns
            var_estimates: VaR estimates (as positive numbers)

        Returns:
            Binary series where 1 indicates VaR breach
        """
        # Exception occurs when loss exceeds VaR
        exceptions = (-actual_returns > var_estimates).astype(int)
        return exceptions

    def kupiec_pof_test(
        self,
        actual_returns: pd.Series,
        var_estimates: pd.Series
    ) -> Dict[str, Union[float, bool]]:
        """
        Kupiec Proportion of Failures (POF) test.

        Tests if the proportion of exceptions is consistent with
        the specified confidence level (unconditional coverage).

        Args:
            actual_returns: Actual portfolio returns
            var_estimates: VaR estimates

        Returns:
            Dictionary with test results
        """
        exceptions = self.calculate_exceptions(actual_returns, var_estimates)
        n = len(exceptions)
        x = exceptions.sum()  # Number of exceptions

        # Expected proportion of failures
        p = self.alpha

        # Observed proportion
        p_hat = x / n

        # Likelihood ratio test statistic
        if x == 0:
            lr_stat = -2 * np.log((1 - p) ** n)
        elif x == n:
            lr_stat = -2 * np.log(p ** n)
        else:
            lr_stat = -2 * (
                n * (p * np.log(p) + (1 - p) * np.log(1 - p)) -
                x * np.log(p_hat) - (n - x) * np.log(1 - p_hat)
            )

        # Chi-square distribution with 1 degree of freedom
        p_value = 1 - stats.chi2.cdf(lr_stat, df=1)

        # Reject null hypothesis if p-value < 0.05
        reject = p_value < 0.05

        return {
            'test': 'Kupiec POF',
            'exceptions': int(x),
            'total_observations': n,
            'exception_rate': p_hat,
            'expected_rate': p,
            'lr_statistic': lr_stat,
            'p_value': p_value,
            'reject_null': reject,
            'interpretation': 'Model REJECTED' if reject else 'Model ACCEPTED'
        }

    def christoffersen_test(
        self,
        actual_returns: pd.Series,
        var_estimates: pd.Series
    ) -> Dict[str, Union[float, bool]]:
        """
        Christoffersen Conditional Coverage test.

        Tests both unconditional coverage and independence of exceptions.

        Args:
            actual_returns: Actual portfolio returns
            var_estimates: VaR estimates

        Returns:
            Dictionary with test results
        """
        exceptions = self.calculate_exceptions(actual_returns, var_estimates)

        # Unconditional coverage (Kupiec test)
        kupiec_result = self.kupiec_pof_test(actual_returns, var_estimates)

        # Independence test
        n = len(exceptions)
        x = exceptions.sum()

        # Count transitions
        n00 = 0  # No exception followed by no exception
        n01 = 0  # No exception followed by exception
        n10 = 0  # Exception followed by no exception
        n11 = 0  # Exception followed by exception

        for i in range(n - 1):
            if exceptions.iloc[i] == 0 and exceptions.iloc[i + 1] == 0:
                n00 += 1
            elif exceptions.iloc[i] == 0 and exceptions.iloc[i + 1] == 1:
                n01 += 1
            elif exceptions.iloc[i] == 1 and exceptions.iloc[i + 1] == 0:
                n10 += 1
            elif exceptions.iloc[i] == 1 and exceptions.iloc[i + 1] == 1:
                n11 += 1

        # Transition probabilities
        if n00 + n01 > 0:
            pi_01 = n01 / (n00 + n01)
        else:
            pi_01 = 0

        if n10 + n11 > 0:
            pi_11 = n11 / (n10 + n11)
        else:
            pi_11 = 0

        pi = x / n

        # Likelihood ratio for independence
        if pi_01 == 0 or pi_11 == 0 or pi == 0 or pi == 1:
            lr_ind = 0
        else:
            lr_ind = -2 * (
                (n00 + n01) * (pi_01 * np.log(pi) + (1 - pi_01) * np.log(1 - pi)) +
                (n10 + n11) * (pi_11 * np.log(pi) + (1 - pi_11) * np.log(1 - pi)) -
                n00 * np.log(1 - pi_01) - n01 * np.log(pi_01) -
                n10 * np.log(1 - pi_11) - n11 * np.log(pi_11)
            )

        # Conditional coverage test statistic
        lr_cc = kupiec_result['lr_statistic'] + lr_ind

        # Chi-square with 2 degrees of freedom
        p_value = 1 - stats.chi2.cdf(lr_cc, df=2)
        reject = p_value < 0.05

        return {
            'test': 'Christoffersen CC',
            'exceptions': int(x),
            'lr_unconditional': kupiec_result['lr_statistic'],
            'lr_independence': lr_ind,
            'lr_cc_statistic': lr_cc,
            'p_value': p_value,
            'reject_null': reject,
            'interpretation': 'Model REJECTED' if reject else 'Model ACCEPTED'
        }

    def traffic_light_test(
        self,
        actual_returns: pd.Series,
        var_estimates: pd.Series
    ) -> Dict[str, Union[int, str]]:
        """
        Basel Traffic Light Approach.

        Categorizes model into green, yellow, or red zone based on
        number of exceptions.

        Args:
            actual_returns: Actual portfolio returns
            var_estimates: VaR estimates

        Returns:
            Dictionary with zone classification
        """
        exceptions = self.calculate_exceptions(actual_returns, var_estimates)
        n_exceptions = exceptions.sum()
        n_obs = len(exceptions)

        # Basel zones (for 250 trading days, 99% VaR)
        # Scaled for actual number of observations
        scale_factor = n_obs / 250

        green_threshold = int(4 * scale_factor)
        yellow_threshold = int(9 * scale_factor)

        if n_exceptions <= green_threshold:
            zone = 'GREEN'
            action = 'No action required'
        elif n_exceptions <= yellow_threshold:
            zone = 'YELLOW'
            action = 'Monitor closely, consider model improvements'
        else:
            zone = 'RED'
            action = 'Model inadequate, immediate revision required'

        return {
            'test': 'Traffic Light',
            'exceptions': int(n_exceptions),
            'total_observations': n_obs,
            'green_threshold': green_threshold,
            'yellow_threshold': yellow_threshold,
            'zone': zone,
            'action': action
        }

    def comprehensive_backtest(
        self,
        actual_returns: pd.Series,
        var_estimates: pd.Series
    ) -> Dict[str, Dict]:
        """
        Run all backtesting procedures.

        Args:
            actual_returns: Actual portfolio returns
            var_estimates: VaR estimates

        Returns:
            Dictionary with all test results
        """
        return {
            'kupiec': self.kupiec_pof_test(actual_returns, var_estimates),
            'christoffersen': self.christoffersen_test(actual_returns, var_estimates),
            'traffic_light': self.traffic_light_test(actual_returns, var_estimates)
        }

    def plot_backtest_results(
        self,
        actual_returns: pd.Series,
        var_estimates: pd.Series
    ) -> pd.DataFrame:
        """
        Prepare data for plotting backtest results.

        Args:
            actual_returns: Actual portfolio returns
            var_estimates: VaR estimates

        Returns:
            DataFrame with returns, VaR, and exceptions
        """
        exceptions = self.calculate_exceptions(actual_returns, var_estimates)

        df = pd.DataFrame({
            'returns': -actual_returns,  # Losses as positive
            'var': var_estimates,
            'exceptions': exceptions
        })

        return df
