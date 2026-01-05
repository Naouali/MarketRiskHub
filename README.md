# Market Risk Hub 📊

A comprehensive market risk analytics engine built in Python, featuring Value at Risk (VaR) calculations, Stressed VaR (SVaR), Expected Shortfall (ES), portfolio optimization, and model backtesting. This project demonstrates professional-grade quantitative risk management techniques used in financial institutions.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

### Risk Calculation Engines
- **Value at Risk (VaR)** - Three methodologies:
  - Historical Simulation
  - Parametric (Variance-Covariance)
  - Monte Carlo Simulation
- **Stressed VaR (SVaR)** - Scenario-based stress testing
- **Expected Shortfall (ES/CVaR)** - Tail risk measurement
- **Component VaR** - Risk contribution decomposition

### Portfolio Analytics
- Performance metrics (returns, Sharpe ratio, Sortino ratio)
- Risk metrics (volatility, max drawdown, Calmar ratio)
- Correlation and covariance analysis
- Portfolio optimization (Maximum Sharpe, Minimum Variance)
- Efficient frontier calculation

### Model Validation
- VaR backtesting framework
- Kupiec POF test (Proportion of Failures)
- Christoffersen test (Conditional Coverage)
- Basel Traffic Light approach

### Data & Visualization
- Yahoo Finance integration for real-time market data
- Interactive Streamlit dashboard
- Plotly visualizations
- Example Jupyter notebooks

## Project Structure

```
MarketRiskHub/
├── src/market_risk_hub/
│   ├── data/                  # Data retrieval and processing
│   │   └── market_data.py
│   ├── risk_engines/          # Risk calculation engines
│   │   ├── var.py            # Value at Risk
│   │   ├── svar.py           # Stressed VaR
│   │   └── expected_shortfall.py
│   ├── portfolio/            # Portfolio analytics
│   │   └── analytics.py
│   ├── backtesting/          # Model validation
│   │   └── var_backtest.py
│   └── utils/                # Utilities
│       └── visualization.py
├── dashboard/                # Streamlit dashboard
│   └── app.py
├── notebooks/                # Example notebooks
│   ├── 01_basic_var_calculation.ipynb
│   ├── 02_portfolio_optimization.ipynb
│   └── 03_var_backtesting.ipynb
├── tests/                    # Unit tests
└── requirements.txt
```

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/MarketRiskHub.git
cd MarketRiskHub
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install the package** (optional, for development)
```bash
pip install -e .
```

## Quick Start

### 1. Basic VaR Calculation

```python
from market_risk_hub.data.market_data import MarketDataFetcher
from market_risk_hub.risk_engines.var import VaRCalculator
import numpy as np

# Fetch market data
fetcher = MarketDataFetcher()
data = fetcher.get_market_data(['AAPL', 'MSFT', 'GOOGL'], period='2y')
returns = data['returns']

# Define portfolio
weights = np.array([0.4, 0.3, 0.3])
portfolio_value = 1_000_000

# Calculate VaR
var_calc = VaRCalculator(confidence_level=0.95)
var_results = var_calc.calculate_all(returns, weights, portfolio_value)

print(f"Historical VaR: ${var_results['historical_var']:,.2f}")
print(f"Parametric VaR: ${var_results['parametric_var']:,.2f}")
print(f"Monte Carlo VaR: ${var_results['monte_carlo_var']:,.2f}")
```

### 2. Portfolio Optimization

```python
from market_risk_hub.portfolio.analytics import PortfolioAnalytics

# Create portfolio analytics
portfolio = PortfolioAnalytics(returns)

# Optimize for maximum Sharpe ratio
optimal = portfolio.optimize_sharpe_ratio(risk_free_rate=0.04)

print(f"Optimal Weights:\n{optimal['weights']}")
print(f"Expected Return: {optimal['return']:.2%}")
print(f"Sharpe Ratio: {optimal['sharpe_ratio']:.4f}")
```

### 3. VaR Backtesting

```python
from market_risk_hub.backtesting.var_backtest import VaRBacktest

# Initialize backtester
backtest = VaRBacktest(confidence_level=0.95)

# Run comprehensive backtest
results = backtest.comprehensive_backtest(actual_returns, var_estimates)

# Check results
print(f"Kupiec Test: {results['kupiec']['interpretation']}")
print(f"Traffic Light Zone: {results['traffic_light']['zone']}")
```

### 4. Launch Interactive Dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard provides:
- Real-time portfolio risk analysis
- Interactive visualizations
- Multiple risk metrics
- Backtesting results
- Portfolio optimization tools

## Example Notebooks

Three comprehensive Jupyter notebooks demonstrate the library's capabilities:

1. **01_basic_var_calculation.ipynb**
   - Data fetching and processing
   - VaR calculation using all methods
   - Component VaR analysis
   - Returns distribution visualization

2. **02_portfolio_optimization.ipynb**
   - Portfolio performance metrics
   - Correlation analysis
   - Efficient frontier
   - Maximum Sharpe and Minimum Variance portfolios

3. **03_var_backtesting.ipynb**
   - Rolling VaR estimation
   - Statistical backtests (Kupiec, Christoffersen)
   - Traffic Light approach
   - Exception analysis

## Risk Metrics Explained

### Value at Risk (VaR)
VaR estimates the maximum potential loss over a given time horizon at a specified confidence level. For example, a 1-day 95% VaR of $100,000 means there's a 95% probability that losses won't exceed $100,000 in one day.

**Methods implemented:**
- **Historical**: Uses empirical distribution of past returns
- **Parametric**: Assumes normal distribution
- **Monte Carlo**: Simulates future scenarios

### Stressed VaR (SVaR)
SVaR measures VaR under stressed market conditions by identifying historical stress periods (high volatility, large drawdowns) and applying those scenarios to the current portfolio.

### Expected Shortfall (ES)
ES (also called CVaR) measures the expected loss given that the VaR threshold has been breached. It provides a more complete picture of tail risk than VaR alone.

### Component VaR
Decomposes total VaR into contributions from individual assets, helping identify the primary sources of portfolio risk.

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/market_risk_hub --cov-report=html

# Run specific test file
pytest tests/test_var.py
```

## Use Cases

### For Portfolio Managers
- Assess portfolio risk exposure
- Optimize asset allocation
- Monitor risk limits
- Generate risk reports

### For Risk Analysts
- Calculate regulatory capital requirements
- Perform stress testing
- Validate risk models
- Analyze historical risk performance

### For Quantitative Researchers
- Research new risk models
- Backtest trading strategies
- Study market risk dynamics
- Compare risk methodologies

## Technical Implementation

### Key Technologies
- **NumPy & Pandas**: Numerical computing and data manipulation
- **SciPy**: Statistical distributions and optimization
- **yfinance**: Market data retrieval
- **Plotly**: Interactive visualizations
- **Streamlit**: Web dashboard framework

### Design Principles
- **Modular architecture**: Separate concerns (data, calculation, visualization)
- **Extensible**: Easy to add new risk metrics or data sources
- **Well-tested**: Comprehensive unit tests for core functionality
- **Production-ready**: Caching, error handling, and validation

## Performance Considerations

- **Data caching**: Historical data cached for 24 hours
- **Vectorized operations**: NumPy for fast calculations
- **Parallel processing**: Multiple simulations run efficiently
- **Optimized algorithms**: SciPy's optimization routines

## Regulatory Context

This project implements risk metrics commonly used in regulatory frameworks:

- **Basel II/III**: VaR for market risk capital requirements
- **Basel Traffic Light**: Model validation approach
- **FRTB**: Stressed VaR for stressed market conditions
- **Solvency II**: Risk measurement for insurance

## Future Enhancements

Potential improvements:
- [ ] Additional risk metrics (Incremental VaR, Marginal VaR)
- [ ] Multi-period VaR
- [ ] Credit risk metrics
- [ ] Real-time data streaming
- [ ] Machine learning-based VaR models
- [ ] Risk reporting templates
- [ ] API endpoints for integration

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Noual Inabil**
- Portfolio demonstrating quantitative risk management expertise
- Built for showcasing market risk analytics skills to recruiters

## Acknowledgments

- Market risk methodologies based on industry best practices
- Inspired by risk management frameworks from leading financial institutions
- Data provided by Yahoo Finance

## Contact

For questions or feedback, please open an issue on GitHub.

---

**Disclaimer**: This project is for educational and demonstration purposes. It should not be used for actual financial decision-making without proper validation and risk management oversight.
