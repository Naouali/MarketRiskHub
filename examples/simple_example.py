"""
Simple example demonstrating the Market Risk Hub library

Run this script to see a quick demonstration of the library's capabilities.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import numpy as np
from market_risk_hub.data.market_data import MarketDataFetcher
from market_risk_hub.risk_engines.var import VaRCalculator
from market_risk_hub.risk_engines.expected_shortfall import ExpectedShortfall
from market_risk_hub.portfolio.analytics import PortfolioAnalytics


def main():
    print("=" * 70)
    print(" Market Risk Hub - Simple Example".center(70))
    print("=" * 70)
    print()

    # 1. Fetch market data
    print("📊 Fetching market data...")
    fetcher = MarketDataFetcher()
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'JPM']
    data = fetcher.get_market_data(tickers, period='1y')
    returns = data['returns']
    print(f"✓ Loaded {len(returns)} days of data for {len(tickers)} assets")
    print()

    # 2. Define portfolio
    weights = np.array([0.25, 0.25, 0.25, 0.25])  # Equal weights
    portfolio_value = 1_000_000
    confidence_level = 0.95

    print(f"💼 Portfolio: ${portfolio_value:,}")
    for ticker, weight in zip(tickers, weights):
        print(f"   {ticker}: {weight:.0%} (${portfolio_value * weight:,.0f})")
    print()

    # 3. Calculate VaR
    print(f"⚠️  Value at Risk ({confidence_level:.0%} Confidence):")
    var_calc = VaRCalculator(confidence_level=confidence_level)
    var_results = var_calc.calculate_all(returns, weights, portfolio_value)

    for method, value in var_results.items():
        print(f"   {method:20s}: ${value:,.2f}")
    print()

    # 4. Calculate Expected Shortfall
    print(f"📉 Expected Shortfall ({confidence_level:.0%} Confidence):")
    es_calc = ExpectedShortfall(confidence_level=confidence_level)
    es_results = es_calc.calculate_all(returns, weights, portfolio_value)

    for method, value in es_results.items():
        print(f"   {method:20s}: ${value:,.2f}")
    print()

    # 5. Component VaR
    print("🔍 Risk Contribution by Asset:")
    component_var = var_calc.var_breakdown(returns, weights) * portfolio_value
    for asset, cvar in component_var.items():
        contribution = (cvar / var_results['historical_var']) * 100
        print(f"   {asset:10s}: ${cvar:,.2f} ({contribution:.1f}%)")
    print()

    # 6. Portfolio metrics
    print("📈 Portfolio Performance Metrics:")
    portfolio = PortfolioAnalytics(returns, weights)
    metrics = portfolio.get_summary(risk_free_rate=0.04)

    key_metrics = [
        'annualized_return',
        'annualized_volatility',
        'sharpe_ratio',
        'max_drawdown'
    ]

    for metric in key_metrics:
        value = metrics[metric]
        if 'return' in metric or 'volatility' in metric or 'drawdown' in metric:
            print(f"   {metric:25s}: {value:.2%}")
        else:
            print(f"   {metric:25s}: {value:.4f}")
    print()

    # 7. Portfolio optimization
    print("🎯 Portfolio Optimization:")
    optimal_sharpe = portfolio.optimize_sharpe_ratio(risk_free_rate=0.04)

    print(f"   Maximum Sharpe Ratio Portfolio:")
    print(f"   Expected Return: {optimal_sharpe['return']:.2%}")
    print(f"   Volatility: {optimal_sharpe['volatility']:.2%}")
    print(f"   Sharpe Ratio: {optimal_sharpe['sharpe_ratio']:.4f}")
    print()
    print(f"   Optimal Weights:")
    for ticker, weight in zip(tickers, optimal_sharpe['weights']):
        print(f"      {ticker}: {weight:.2%}")
    print()

    print("=" * 70)
    print("✓ Analysis complete!".center(70))
    print()
    print("Next steps:")
    print("  • Launch the dashboard: streamlit run dashboard/app.py")
    print("  • Explore notebooks in the notebooks/ directory")
    print("  • Run tests: pytest tests/")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nMake sure you have:")
        print("  1. Installed all requirements: pip install -r requirements.txt")
        print("  2. An active internet connection (for fetching data)")
        sys.exit(1)
