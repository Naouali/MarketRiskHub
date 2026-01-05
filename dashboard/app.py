"""
Market Risk Hub - Interactive Dashboard
Run with: streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from market_risk_hub.data.market_data import MarketDataFetcher
from market_risk_hub.risk_engines.var import VaRCalculator
from market_risk_hub.risk_engines.svar import StressedVaR
from market_risk_hub.risk_engines.expected_shortfall import ExpectedShortfall
from market_risk_hub.portfolio.analytics import PortfolioAnalytics
from market_risk_hub.backtesting.var_backtest import VaRBacktest
from market_risk_hub.utils.visualization import RiskVisualizer


# Page configuration
st.set_page_config(
    page_title="Market Risk Hub",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False


def main():
    """Main dashboard application."""

    # Header
    st.markdown('<h1 class="main-header">📊 Market Risk Analytics Hub</h1>', unsafe_allow_html=True)
    st.markdown("---")

    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")

    # Portfolio selection
    st.sidebar.subheader("Portfolio Selection")

    preset_portfolios = {
        "Tech Portfolio": ["AAPL", "MSFT", "GOOGL", "AMZN"],
        "Diversified": ["SPY", "TLT", "GLD", "VNQ"],
        "FAANG": ["META", "AAPL", "AMZN", "NFLX", "GOOGL"],
        "Custom": []
    }

    portfolio_type = st.sidebar.selectbox("Select Portfolio Type", list(preset_portfolios.keys()))

    if portfolio_type == "Custom":
        tickers_input = st.sidebar.text_input(
            "Enter tickers (comma-separated)",
            "AAPL,MSFT,GOOGL,JPM,GLD"
        )
        tickers = [t.strip().upper() for t in tickers_input.split(",")]
    else:
        tickers = preset_portfolios[portfolio_type]
        st.sidebar.write(f"Tickers: {', '.join(tickers)}")

    # Time period
    st.sidebar.subheader("Time Period")
    period = st.sidebar.selectbox(
        "Historical Data Period",
        ["1y", "2y", "5y", "10y"],
        index=1
    )

    # Risk parameters
    st.sidebar.subheader("Risk Parameters")
    confidence_level = st.sidebar.slider(
        "Confidence Level",
        min_value=0.90,
        max_value=0.99,
        value=0.95,
        step=0.01
    )

    portfolio_value = st.sidebar.number_input(
        "Portfolio Value ($)",
        min_value=1000,
        max_value=10000000,
        value=1000000,
        step=10000
    )

    # Load data button
    if st.sidebar.button("🔄 Load Data", type="primary"):
        with st.spinner("Fetching market data..."):
            try:
                fetcher = MarketDataFetcher()
                data = fetcher.get_market_data(tickers, period=period)
                st.session_state.prices = data['prices']
                st.session_state.returns = data['returns']
                st.session_state.tickers = tickers
                st.session_state.data_loaded = True
                st.sidebar.success("✅ Data loaded successfully!")
            except Exception as e:
                st.sidebar.error(f"❌ Error loading data: {str(e)}")
                return

    # Main content
    if not st.session_state.data_loaded:
        st.info("👈 Configure your portfolio in the sidebar and click 'Load Data' to begin analysis.")

        # Show example use case
        st.subheader("📚 About Market Risk Hub")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            **Risk Calculation**
            - Value at Risk (VaR)
            - Stressed VaR (SVaR)
            - Expected Shortfall (ES)
            - Multiple methodologies
            """)

        with col2:
            st.markdown("""
            **Portfolio Analytics**
            - Performance metrics
            - Risk metrics
            - Correlation analysis
            - Portfolio optimization
            """)

        with col3:
            st.markdown("""
            **Model Validation**
            - VaR backtesting
            - Kupiec POF test
            - Christoffersen test
            - Traffic light approach
            """)

        return

    # Tabs for different analyses
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview",
        "⚠️ Risk Metrics",
        "📊 Portfolio Analytics",
        "🔬 Backtesting",
        "🎯 Optimization"
    ])

    returns = st.session_state.returns
    prices = st.session_state.prices

    # Equal weights for simplicity
    weights = np.array([1.0 / len(tickers)] * len(tickers))

    # Tab 1: Overview
    with tab1:
        st.header("Portfolio Overview")

        # Price chart
        st.subheader("Price History (Normalized)")
        normalized_prices = prices / prices.iloc[0] * 100
        st.line_chart(normalized_prices)

        # Summary statistics
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Asset Statistics")
            stats_df = pd.DataFrame({
                'Mean Return': returns.mean() * 252,
                'Volatility': returns.std() * np.sqrt(252),
                'Sharpe Ratio': (returns.mean() * 252) / (returns.std() * np.sqrt(252))
            })
            st.dataframe(stats_df.style.format("{:.4f}"))

        with col2:
            st.subheader("Correlation Matrix")
            corr_matrix = returns.corr()
            st.dataframe(corr_matrix.style.background_gradient(cmap='RdYlGn', vmin=-1, vmax=1).format("{:.2f}"))

        # Correlation heatmap
        st.subheader("Correlation Heatmap")
        fig = RiskVisualizer.plot_correlation_heatmap(corr_matrix)
        st.plotly_chart(fig, use_container_width=True)

    # Tab 2: Risk Metrics
    with tab2:
        st.header("Risk Metrics Analysis")

        # Calculate VaR
        var_calc = VaRCalculator(confidence_level=confidence_level)
        var_results = var_calc.calculate_all(returns, weights, portfolio_value)

        # Calculate ES
        es_calc = ExpectedShortfall(confidence_level=confidence_level)
        es_results = es_calc.calculate_all(returns, weights, portfolio_value)

        # Calculate SVaR
        svar_calc = StressedVaR(confidence_level=confidence_level)
        try:
            svar_scenarios = svar_calc.stress_test_scenarios(returns, weights)
            svar_scenarios = {k: v * portfolio_value for k, v in svar_scenarios.items() if not np.isnan(v)}
        except:
            svar_scenarios = {}

        # Display metrics
        st.subheader(f"Value at Risk ({confidence_level:.0%} Confidence)")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Historical VaR", f"${var_results['historical_var']:,.2f}")
        with col2:
            st.metric("Parametric VaR", f"${var_results['parametric_var']:,.2f}")
        with col3:
            st.metric("Monte Carlo VaR", f"${var_results['monte_carlo_var']:,.2f}")

        # VaR comparison chart
        st.subheader("VaR Method Comparison")
        fig = RiskVisualizer.plot_var_comparison(var_results, "VaR Comparison ($ Values)")
        st.plotly_chart(fig, use_container_width=True)

        # Expected Shortfall
        st.subheader(f"Expected Shortfall ({confidence_level:.0%} Confidence)")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Historical ES", f"${es_results['historical_es']:,.2f}")
        with col2:
            st.metric("Parametric ES", f"${es_results['parametric_es']:,.2f}")
        with col3:
            st.metric("Monte Carlo ES", f"${es_results['monte_carlo_es']:,.2f}")

        # ES/VaR ratio
        es_var_ratio = es_results['historical_es'] / var_results['historical_var']
        st.metric("ES/VaR Ratio", f"{es_var_ratio:.2f}",
                 help="Higher ratio indicates more severe tail risk")

        # Stressed VaR
        if svar_scenarios:
            st.subheader("Stressed VaR Scenarios")
            svar_df = pd.DataFrame.from_dict(svar_scenarios, orient='index', columns=['SVaR'])
            svar_df.index.name = 'Scenario'
            st.dataframe(svar_df.style.format("${:,.2f}"))

        # Returns distribution
        st.subheader("Returns Distribution")
        portfolio_returns = (returns * weights).sum(axis=1)
        fig = RiskVisualizer.plot_returns_distribution(
            portfolio_returns,
            var_results['historical_var'] / portfolio_value,
            es_results['historical_es'] / portfolio_value
        )
        st.plotly_chart(fig, use_container_width=True)

        # Component VaR
        st.subheader("Risk Contribution by Asset")
        component_var = var_calc.var_breakdown(returns, weights) * portfolio_value
        fig = RiskVisualizer.plot_component_var(component_var)
        st.plotly_chart(fig, use_container_width=True)

    # Tab 3: Portfolio Analytics
    with tab3:
        st.header("Portfolio Analytics")

        portfolio = PortfolioAnalytics(returns, weights)

        # Portfolio metrics
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Return Metrics")
            return_metrics = portfolio.calculate_returns_metrics()
            metrics_df = pd.DataFrame.from_dict(return_metrics, orient='index', columns=['Value'])
            st.dataframe(metrics_df.style.format("{:.4f}"))

        with col2:
            st.subheader("Risk Metrics")
            risk_metrics = portfolio.calculate_risk_metrics()
            risk_df = pd.DataFrame.from_dict(risk_metrics, orient='index', columns=['Value'])
            st.dataframe(risk_df.style.format("{:.4f}"))

        # Cumulative returns
        st.subheader("Cumulative Returns")
        fig = RiskVisualizer.plot_cumulative_returns(portfolio.portfolio_returns)
        st.plotly_chart(fig, use_container_width=True)

        # Portfolio weights
        st.subheader("Current Portfolio Allocation")
        weights_df = pd.DataFrame({
            'Asset': tickers,
            'Weight': weights,
            'Value': weights * portfolio_value
        })
        st.dataframe(weights_df.style.format({'Weight': '{:.2%}', 'Value': '${:,.2f}'}))

    # Tab 4: Backtesting
    with tab4:
        st.header("VaR Model Backtesting")

        # Calculate rolling VaR
        window = 252  # 1 year rolling window
        rolling_var = []
        actual_returns = []

        for i in range(window, len(returns)):
            historical_returns = returns.iloc[i-window:i]
            var = var_calc.historical_var(historical_returns, weights)
            rolling_var.append(var)
            actual_returns.append((returns.iloc[i] * weights).sum())

        rolling_var = pd.Series(rolling_var, index=returns.index[window:])
        actual_returns = pd.Series(actual_returns, index=returns.index[window:])

        # Run backtests
        backtest = VaRBacktest(confidence_level=confidence_level)
        results = backtest.comprehensive_backtest(actual_returns, rolling_var)

        # Display test results
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Kupiec POF Test")
            kupiec = results['kupiec']
            st.metric("Exceptions", kupiec['exceptions'])
            st.metric("Exception Rate", f"{kupiec['exception_rate']:.2%}")
            st.metric("P-Value", f"{kupiec['p_value']:.4f}")
            if kupiec['reject_null']:
                st.error(kupiec['interpretation'])
            else:
                st.success(kupiec['interpretation'])

        with col2:
            st.subheader("Christoffersen Test")
            cc = results['christoffersen']
            st.metric("LR Statistic", f"{cc['lr_cc_statistic']:.4f}")
            st.metric("P-Value", f"{cc['p_value']:.4f}")
            if cc['reject_null']:
                st.error(cc['interpretation'])
            else:
                st.success(cc['interpretation'])

        with col3:
            st.subheader("Traffic Light Test")
            tl = results['traffic_light']
            st.metric("Zone", tl['zone'])
            st.metric("Exceptions", tl['exceptions'])

            if tl['zone'] == 'GREEN':
                st.success(tl['action'])
            elif tl['zone'] == 'YELLOW':
                st.warning(tl['action'])
            else:
                st.error(tl['action'])

        # Backtest visualization
        st.subheader("VaR Backtesting Results")
        backtest_df = backtest.plot_backtest_results(actual_returns, rolling_var)
        fig = RiskVisualizer.plot_backtest_results(backtest_df)
        st.plotly_chart(fig, use_container_width=True)

    # Tab 5: Optimization
    with tab5:
        st.header("Portfolio Optimization")

        portfolio = PortfolioAnalytics(returns)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Maximum Sharpe Ratio Portfolio")
            with st.spinner("Optimizing..."):
                optimal_sharpe = portfolio.optimize_sharpe_ratio()

            st.write("**Optimal Weights:**")
            st.dataframe(optimal_sharpe['weights'].to_frame('Weight').style.format("{:.2%}"))

            st.metric("Expected Return", f"{optimal_sharpe['return']:.2%}")
            st.metric("Volatility", f"{optimal_sharpe['volatility']:.2%}")
            st.metric("Sharpe Ratio", f"{optimal_sharpe['sharpe_ratio']:.4f}")

        with col2:
            st.subheader("Minimum Variance Portfolio")
            with st.spinner("Optimizing..."):
                min_var = portfolio.optimize_minimum_variance()

            st.write("**Optimal Weights:**")
            st.dataframe(min_var['weights'].to_frame('Weight').style.format("{:.2%}"))

            st.metric("Expected Return", f"{min_var['return']:.2%}")
            st.metric("Volatility", f"{min_var['volatility']:.2%}")

        # Efficient Frontier
        st.subheader("Efficient Frontier")
        with st.spinner("Calculating efficient frontier..."):
            ef_returns, ef_vols, ef_sharpes = portfolio.efficient_frontier(n_portfolios=50)

        current_portfolio_metrics = {
            'return': (returns * weights).sum(axis=1).mean() * 252,
            'volatility': (returns * weights).sum(axis=1).std() * np.sqrt(252)
        }

        fig = RiskVisualizer.plot_efficient_frontier(
            ef_returns, ef_vols, ef_sharpes, current_portfolio_metrics
        )
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
