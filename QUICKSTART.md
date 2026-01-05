# Quick Start Guide

Get started with Market Risk Hub in 5 minutes!

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/MarketRiskHub.git
cd MarketRiskHub

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Option 1: Run the Example Script (Fastest)

```bash
python examples/simple_example.py
```

This will:
- Fetch real market data
- Calculate VaR, SVaR, and ES
- Show portfolio metrics
- Display risk contributions
- Demonstrate optimization

**Expected output:**
```
======================================================================
               Market Risk Hub - Simple Example
======================================================================

📊 Fetching market data...
✓ Loaded 252 days of data for 4 assets

💼 Portfolio: $1,000,000
   AAPL: 25% ($250,000)
   MSFT: 25% ($250,000)
   GOOGL: 25% ($250,000)
   JPM: 25% ($250,000)

⚠️  Value at Risk (95% Confidence):
   historical_var      : $18,456.23
   parametric_var      : $17,234.56
   monte_carlo_var     : $18,123.45

...
```

## Option 2: Launch Interactive Dashboard

```bash
streamlit run dashboard/app.py
```

Then open your browser to `http://localhost:8501`

**Features:**
- Real-time portfolio analysis
- Interactive charts
- Multiple risk metrics
- Backtesting results
- Portfolio optimization

## Option 3: Jupyter Notebooks

```bash
jupyter notebook
```

Navigate to the `notebooks/` directory and open:
1. `01_basic_var_calculation.ipynb` - VaR fundamentals
2. `02_portfolio_optimization.ipynb` - Portfolio optimization
3. `03_var_backtesting.ipynb` - Model validation

## Option 4: Python API

### Simple VaR Calculation

```python
from market_risk_hub.data.market_data import MarketDataFetcher
from market_risk_hub.risk_engines.var import VaRCalculator
import numpy as np

# Fetch data
fetcher = MarketDataFetcher()
data = fetcher.get_market_data(['AAPL', 'MSFT'], period='1y')
returns = data['returns']

# Calculate VaR
var_calc = VaRCalculator(confidence_level=0.95)
weights = np.array([0.5, 0.5])
var = var_calc.historical_var(returns, weights)

print(f"95% VaR: {var:.4f}")
```

### Portfolio Optimization

```python
from market_risk_hub.portfolio.analytics import PortfolioAnalytics

portfolio = PortfolioAnalytics(returns)
optimal = portfolio.optimize_sharpe_ratio(risk_free_rate=0.04)

print(f"Optimal Sharpe: {optimal['sharpe_ratio']:.4f}")
print(f"Optimal Weights:\n{optimal['weights']}")
```

### VaR Backtesting

```python
from market_risk_hub.backtesting.var_backtest import VaRBacktest

backtest = VaRBacktest(confidence_level=0.95)
results = backtest.comprehensive_backtest(actual_returns, var_estimates)

print(f"Kupiec Test: {results['kupiec']['interpretation']}")
print(f"Zone: {results['traffic_light']['zone']}")
```

## Common Use Cases

### 1. Daily Risk Report

```python
# Fetch latest data
data = fetcher.get_market_data(tickers, period='1y')
returns = data['returns']

# Calculate all risk metrics
var_calc = VaRCalculator(confidence_level=0.95)
var_results = var_calc.calculate_all(returns, weights, portfolio_value)

es_calc = ExpectedShortfall(confidence_level=0.95)
es_results = es_calc.calculate_all(returns, weights, portfolio_value)

# Generate report
print(f"Portfolio Value: ${portfolio_value:,}")
print(f"95% VaR: ${var_results['historical_var']:,}")
print(f"95% ES: ${es_results['historical_es']:,}")
```

### 2. Portfolio Rebalancing

```python
# Analyze current portfolio
portfolio = PortfolioAnalytics(returns, current_weights)
current_metrics = portfolio.get_summary()

# Find optimal allocation
optimal = portfolio.optimize_sharpe_ratio()

# Compare
print("Current Sharpe:", current_metrics['sharpe_ratio'])
print("Optimal Sharpe:", optimal['sharpe_ratio'])
print("\nSuggested Rebalancing:")
print(optimal['weights'] - current_weights)
```

### 3. Stress Testing

```python
from market_risk_hub.risk_engines.svar import StressedVaR

svar_calc = StressedVaR(confidence_level=0.95)
scenarios = svar_calc.stress_test_scenarios(returns, weights)

for scenario, value in scenarios.items():
    print(f"{scenario}: ${value:,.2f}")
```

## Available Commands (Makefile)

```bash
make install        # Install dependencies
make test          # Run tests
make run-dashboard # Launch dashboard
make run-example   # Run example script
make clean         # Clean cache files
```

## Troubleshooting

### Import Error

**Problem**: `ModuleNotFoundError: No module named 'market_risk_hub'`

**Solution**: Install the package
```bash
pip install -e .
```

### Data Fetch Error

**Problem**: `Error fetching data from Yahoo Finance`

**Solutions**:
- Check internet connection
- Try different tickers
- Reduce time period
- Wait and retry (rate limiting)

### Dashboard Won't Load

**Problem**: Dashboard shows errors

**Solution**: Install Streamlit
```bash
pip install streamlit
```

## Next Steps

1. **Customize**: Modify portfolios and parameters in examples
2. **Extend**: Add new risk metrics or data sources
3. **Integrate**: Use in your own risk management workflows
4. **Learn**: Read the [METHODOLOGY.md](docs/METHODOLOGY.md) for theory

## Getting Help

- Check [README.md](README.md) for detailed documentation
- Review [CONTRIBUTING.md](CONTRIBUTING.md) for development
- Open an issue on GitHub for bugs/questions
- Explore notebooks for in-depth examples

## Demo Portfolio Suggestions

### Conservative
```python
tickers = ['TLT', 'GLD', 'VNQ']  # Bonds, Gold, Real Estate
weights = [0.5, 0.3, 0.2]
```

### Growth
```python
tickers = ['QQQ', 'SPY', 'IWM']  # Nasdaq, S&P 500, Small Caps
weights = [0.4, 0.4, 0.2]
```

### Tech Heavy
```python
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
weights = [0.2, 0.2, 0.2, 0.2, 0.2]
```

### Diversified
```python
tickers = ['SPY', 'TLT', 'GLD', 'VNQ', 'DBC']  # Stocks, Bonds, Gold, RE, Commodities
weights = [0.3, 0.3, 0.2, 0.1, 0.1]
```

Happy analyzing! 📊
