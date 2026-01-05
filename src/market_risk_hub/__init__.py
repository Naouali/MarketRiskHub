"""
Market Risk Hub - Comprehensive Risk Analytics Engine
"""

__version__ = "1.0.0"

from .data.market_data import MarketDataFetcher
from .risk_engines.var import VaRCalculator
from .risk_engines.svar import StressedVaR
from .risk_engines.expected_shortfall import ExpectedShortfall
from .portfolio.analytics import PortfolioAnalytics

__all__ = [
    'MarketDataFetcher',
    'VaRCalculator',
    'StressedVaR',
    'ExpectedShortfall',
    'PortfolioAnalytics',
]
