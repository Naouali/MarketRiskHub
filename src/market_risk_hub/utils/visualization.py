"""
Visualization utilities for risk metrics
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, Optional, List


class RiskVisualizer:
    """
    Create interactive visualizations for risk metrics.
    """

    @staticmethod
    def plot_var_comparison(var_results: Dict[str, float], title: str = "VaR Comparison") -> go.Figure:
        """
        Create bar chart comparing different VaR methods.

        Args:
            var_results: Dictionary with VaR values from different methods
            title: Chart title

        Returns:
            Plotly figure
        """
        fig = go.Figure(data=[
            go.Bar(
                x=list(var_results.keys()),
                y=list(var_results.values()),
                text=[f"{v:.4f}" for v in var_results.values()],
                textposition='auto',
            )
        ])

        fig.update_layout(
            title=title,
            xaxis_title="Method",
            yaxis_title="VaR",
            template="plotly_white"
        )

        return fig

    @staticmethod
    def plot_efficient_frontier(
        returns: np.ndarray,
        volatilities: np.ndarray,
        sharpe_ratios: np.ndarray,
        current_portfolio: Optional[Dict] = None
    ) -> go.Figure:
        """
        Plot the efficient frontier.

        Args:
            returns: Portfolio returns
            volatilities: Portfolio volatilities
            sharpe_ratios: Sharpe ratios
            current_portfolio: Current portfolio metrics (optional)

        Returns:
            Plotly figure
        """
        fig = go.Figure()

        # Efficient frontier
        fig.add_trace(go.Scatter(
            x=volatilities,
            y=returns,
            mode='markers',
            marker=dict(
                size=8,
                color=sharpe_ratios,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Sharpe Ratio")
            ),
            text=[f"Return: {r:.2%}<br>Vol: {v:.2%}<br>Sharpe: {s:.2f}"
                  for r, v, s in zip(returns, volatilities, sharpe_ratios)],
            hovertemplate='%{text}<extra></extra>',
            name='Efficient Frontier'
        ))

        # Current portfolio
        if current_portfolio:
            fig.add_trace(go.Scatter(
                x=[current_portfolio['volatility']],
                y=[current_portfolio['return']],
                mode='markers',
                marker=dict(size=15, color='red', symbol='star'),
                name='Current Portfolio'
            ))

        fig.update_layout(
            title="Efficient Frontier",
            xaxis_title="Volatility (Annual)",
            yaxis_title="Expected Return (Annual)",
            template="plotly_white",
            hovermode='closest'
        )

        return fig

    @staticmethod
    def plot_returns_distribution(
        returns: pd.Series,
        var_value: Optional[float] = None,
        es_value: Optional[float] = None
    ) -> go.Figure:
        """
        Plot returns distribution with VaR and ES markers.

        Args:
            returns: Return series
            var_value: VaR value to mark (optional)
            es_value: Expected Shortfall value to mark (optional)

        Returns:
            Plotly figure
        """
        fig = go.Figure()

        # Histogram
        fig.add_trace(go.Histogram(
            x=returns,
            nbinsx=50,
            name='Returns Distribution',
            histnorm='probability density'
        ))

        # VaR line
        if var_value is not None:
            fig.add_vline(
                x=-var_value,
                line_dash="dash",
                line_color="red",
                annotation_text=f"VaR: {var_value:.4f}",
                annotation_position="top"
            )

        # ES line
        if es_value is not None:
            fig.add_vline(
                x=-es_value,
                line_dash="dash",
                line_color="orange",
                annotation_text=f"ES: {es_value:.4f}",
                annotation_position="bottom"
            )

        fig.update_layout(
            title="Returns Distribution",
            xaxis_title="Returns",
            yaxis_title="Density",
            template="plotly_white",
            showlegend=True
        )

        return fig

    @staticmethod
    def plot_correlation_heatmap(correlation_matrix: pd.DataFrame) -> go.Figure:
        """
        Create correlation heatmap.

        Args:
            correlation_matrix: Correlation matrix

        Returns:
            Plotly figure
        """
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            colorscale='RdBu',
            zmid=0,
            text=correlation_matrix.values,
            texttemplate='%{text:.2f}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))

        fig.update_layout(
            title="Asset Correlation Matrix",
            template="plotly_white",
            height=600,
            width=800
        )

        return fig

    @staticmethod
    def plot_backtest_results(backtest_df: pd.DataFrame) -> go.Figure:
        """
        Plot VaR backtesting results.

        Args:
            backtest_df: DataFrame with returns, VaR, and exceptions

        Returns:
            Plotly figure
        """
        fig = go.Figure()

        # Actual losses
        fig.add_trace(go.Scatter(
            x=backtest_df.index,
            y=backtest_df['returns'],
            mode='lines',
            name='Actual Losses',
            line=dict(color='blue', width=1)
        ))

        # VaR threshold
        fig.add_trace(go.Scatter(
            x=backtest_df.index,
            y=backtest_df['var'],
            mode='lines',
            name='VaR Threshold',
            line=dict(color='red', width=2, dash='dash')
        ))

        # Exceptions
        exceptions_df = backtest_df[backtest_df['exceptions'] == 1]
        fig.add_trace(go.Scatter(
            x=exceptions_df.index,
            y=exceptions_df['returns'],
            mode='markers',
            name='VaR Breaches',
            marker=dict(color='red', size=10, symbol='x')
        ))

        fig.update_layout(
            title="VaR Backtesting Results",
            xaxis_title="Date",
            yaxis_title="Loss",
            template="plotly_white",
            hovermode='x unified'
        )

        return fig

    @staticmethod
    def plot_component_var(component_var: pd.Series, title: str = "Component VaR") -> go.Figure:
        """
        Plot component VaR breakdown.

        Args:
            component_var: Series with component VaR for each asset
            title: Chart title

        Returns:
            Plotly figure
        """
        fig = go.Figure(data=[
            go.Bar(
                x=component_var.index,
                y=component_var.values,
                text=[f"{v:.4f}" for v in component_var.values],
                textposition='auto',
            )
        ])

        fig.update_layout(
            title=title,
            xaxis_title="Asset",
            yaxis_title="Component VaR",
            template="plotly_white"
        )

        return fig

    @staticmethod
    def plot_cumulative_returns(returns: pd.Series, benchmark: Optional[pd.Series] = None) -> go.Figure:
        """
        Plot cumulative returns.

        Args:
            returns: Portfolio returns
            benchmark: Benchmark returns (optional)

        Returns:
            Plotly figure
        """
        fig = go.Figure()

        # Portfolio cumulative returns
        cumulative_returns = (1 + returns).cumprod()
        fig.add_trace(go.Scatter(
            x=cumulative_returns.index,
            y=cumulative_returns.values,
            mode='lines',
            name='Portfolio',
            line=dict(color='blue', width=2)
        ))

        # Benchmark cumulative returns
        if benchmark is not None:
            cumulative_benchmark = (1 + benchmark).cumprod()
            fig.add_trace(go.Scatter(
                x=cumulative_benchmark.index,
                y=cumulative_benchmark.values,
                mode='lines',
                name='Benchmark',
                line=dict(color='gray', width=2, dash='dash')
            ))

        fig.update_layout(
            title="Cumulative Returns",
            xaxis_title="Date",
            yaxis_title="Cumulative Return",
            template="plotly_white",
            hovermode='x unified'
        )

        return fig

    @staticmethod
    def create_risk_dashboard(
        returns: pd.DataFrame,
        weights: np.ndarray,
        var_results: Dict[str, float],
        portfolio_metrics: pd.Series
    ) -> go.Figure:
        """
        Create comprehensive risk dashboard with subplots.

        Args:
            returns: Returns DataFrame
            weights: Portfolio weights
            var_results: VaR calculation results
            portfolio_metrics: Portfolio metrics

        Returns:
            Plotly figure with subplots
        """
        from plotly.subplots import make_subplots

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("VaR Comparison", "Returns Distribution",
                          "Correlation Matrix", "Portfolio Weights"),
            specs=[[{"type": "bar"}, {"type": "histogram"}],
                   [{"type": "heatmap"}, {"type": "pie"}]]
        )

        # VaR Comparison
        fig.add_trace(
            go.Bar(x=list(var_results.keys()), y=list(var_results.values())),
            row=1, col=1
        )

        # Returns Distribution
        portfolio_returns = (returns * weights).sum(axis=1)
        fig.add_trace(
            go.Histogram(x=portfolio_returns, nbinsx=50),
            row=1, col=2
        )

        # Correlation Matrix
        corr_matrix = returns.corr()
        fig.add_trace(
            go.Heatmap(z=corr_matrix.values, x=corr_matrix.columns, y=corr_matrix.index),
            row=2, col=1
        )

        # Portfolio Weights
        fig.add_trace(
            go.Pie(labels=returns.columns, values=weights),
            row=2, col=2
        )

        fig.update_layout(
            height=800,
            title_text="Risk Analytics Dashboard",
            showlegend=False,
            template="plotly_white"
        )

        return fig
