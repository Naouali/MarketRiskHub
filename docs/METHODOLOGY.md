# Risk Methodology Documentation

This document explains the mathematical foundations and methodologies used in the Market Risk Hub.

## Table of Contents
1. [Value at Risk (VaR)](#value-at-risk-var)
2. [Stressed VaR (SVaR)](#stressed-var-svar)
3. [Expected Shortfall (ES)](#expected-shortfall-es)
4. [Portfolio Optimization](#portfolio-optimization)
5. [Backtesting](#backtesting)

---

## Value at Risk (VaR)

VaR is a statistical measure that quantifies the level of financial risk within a portfolio over a specific time frame.

### Definition

VaR at confidence level α is defined as:

```
P(Loss ≤ VaR_α) = α
```

Where:
- α = confidence level (e.g., 0.95 for 95%)
- Loss = portfolio loss over the holding period

### Methodologies

#### 1. Historical Simulation VaR

**Approach**: Uses empirical distribution of historical returns.

**Calculation**:
```
VaR_α = -Percentile(returns, 1-α)
```

**Advantages**:
- Non-parametric (no distribution assumptions)
- Captures actual market behavior
- Handles non-normal distributions

**Disadvantages**:
- Assumes past repeats future
- Requires significant historical data
- Slow to adapt to regime changes

#### 2. Parametric VaR (Variance-Covariance)

**Approach**: Assumes returns follow a normal distribution.

**Calculation**:
```
VaR_α = -(μ + z_α × σ)
```

Where:
- μ = mean return
- σ = standard deviation of returns
- z_α = standard normal quantile at confidence level α

**For portfolios**:
```
σ_p = √(w^T × Σ × w)
```

Where:
- w = portfolio weights vector
- Σ = covariance matrix

**Advantages**:
- Fast computation
- Mathematically tractable
- Requires less data

**Disadvantages**:
- Assumes normality (fails with fat tails)
- Underestimates risk in crisis periods
- Sensitive to estimation error

#### 3. Monte Carlo VaR

**Approach**: Simulates future returns based on estimated parameters.

**Calculation**:
1. Estimate return distribution parameters (μ, Σ)
2. Generate N random scenarios
3. Calculate portfolio returns for each scenario
4. VaR = percentile of simulated distribution

**Advantages**:
- Flexible (can model complex distributions)
- Handles non-linear instruments
- Can incorporate various risk factors

**Disadvantages**:
- Computationally intensive
- Results depend on model assumptions
- Requires more expertise

### Component VaR

Component VaR decomposes total VaR into individual asset contributions.

**Marginal VaR** (change in VaR from small position change):
```
MVaR_i = (Cov(R_i, R_p)) / σ_p
```

**Component VaR**:
```
CVaR_i = w_i × MVaR_i
```

**Properties**:
- Sum of component VaRs equals total VaR
- Identifies main risk contributors
- Useful for risk budgeting

---

## Stressed VaR (SVaR)

SVaR measures VaR under stressed market conditions.

### Methodology

1. **Identify stress period**: Historical periods of:
   - High volatility
   - Large drawdowns
   - High correlation (contagion)

2. **Calculate VaR using stress period returns**:
```
SVaR_α = -Percentile(stress_returns, 1-α)
```

### Stress Period Identification

**Volatility-based**:
```
Stress if: σ_rolling > Percentile(σ_rolling, 95%)
```

**Drawdown-based**:
```
DD_t = (P_t - max(P_0...t)) / max(P_0...t)
Stress if: DD_t < Percentile(DD, 5%)
```

**Correlation-based**:
```
Stress if: avg_corr > Percentile(corr_rolling, 95%)
```

### Applications

- Regulatory capital (FRTB)
- Stress testing
- Crisis scenario analysis
- Risk limit setting

---

## Expected Shortfall (ES)

ES measures the expected loss given that VaR threshold is breached.

### Definition

```
ES_α = E[Loss | Loss > VaR_α]
```

### Calculation Methods

#### 1. Historical ES

```
ES_α = -mean(returns[returns < -VaR_α])
```

#### 2. Parametric ES (Normal distribution)

```
ES_α = -(μ - σ × φ(Φ^(-1)(α)) / α)
```

Where:
- φ = standard normal PDF
- Φ = standard normal CDF

#### 3. Monte Carlo ES

```
ES_α = -mean(simulated_returns[simulated_returns < -VaR_α])
```

### ES/VaR Ratio

```
Ratio = ES / VaR
```

- Ratio > 1 (always)
- Higher ratio indicates fatter tails
- Typical range: 1.1 - 1.5

### Advantages over VaR

- Coherent risk measure
- Captures tail risk severity
- Preferred by Basel III

---

## Portfolio Optimization

### Mean-Variance Optimization

**Objective**: Minimize variance for target return

```
min: σ_p^2 = w^T × Σ × w
subject to:
  w^T × μ = r_target
  sum(w) = 1
  w ≥ 0
```

### Maximum Sharpe Ratio

**Objective**: Maximize risk-adjusted returns

```
max: SR = (r_p - r_f) / σ_p
where:
  r_p = w^T × μ
  σ_p = √(w^T × Σ × w)
```

### Minimum Variance Portfolio

**Objective**: Find portfolio with lowest risk

```
min: σ_p^2 = w^T × Σ × w
subject to: sum(w) = 1, w ≥ 0
```

### Efficient Frontier

Set of portfolios offering:
- Maximum return for given risk
- Minimum risk for given return

**Construction**:
1. Solve optimization for range of target returns
2. Plot risk vs return
3. Identify optimal portfolios

---

## Backtesting

Validates VaR model accuracy using historical data.

### Kupiec POF Test

**Hypothesis**: Exception rate equals expected rate

**Test statistic**:
```
LR = -2 × [n×(p×ln(p) + (1-p)×ln(1-p)) - x×ln(x/n) - (n-x)×ln(1-x/n)]
```

Where:
- n = number of observations
- x = number of exceptions
- p = expected exception rate (1-α)

**Distribution**: χ²(1) under null hypothesis

**Decision**: Reject if p-value < 0.05

### Christoffersen Test

**Tests**:
1. Unconditional coverage (Kupiec)
2. Independence of exceptions

**Test statistic**:
```
LR_CC = LR_UC + LR_IND
```

**Distribution**: χ²(2)

**Interpretation**:
- Reject if exceptions are clustered
- Indicates model doesn't capture volatility clustering

### Traffic Light Approach

**Basel zones** (for 250 days, 99% VaR):
- Green: ≤ 4 exceptions (good model)
- Yellow: 5-9 exceptions (monitor)
- Red: ≥ 10 exceptions (inadequate model)

**Action**:
- Green: No action
- Yellow: Improve model
- Red: Immediate revision required

---

## Performance Metrics

### Sharpe Ratio

```
SR = (r_p - r_f) / σ_p
```

Measures excess return per unit of risk.

### Sortino Ratio

```
Sortino = (r_p - r_f) / σ_downside
```

Only penalizes downside volatility.

### Maximum Drawdown

```
DD_t = (P_t - max(P_0...t)) / max(P_0...t)
MDD = min(DD_t)
```

### Calmar Ratio

```
Calmar = annualized_return / |MDD|
```

---

## References

1. **Basel Committee on Banking Supervision** (2019). "Minimum capital requirements for market risk"

2. **Jorion, P.** (2006). "Value at Risk: The New Benchmark for Managing Financial Risk"

3. **McNeil, A. J., Frey, R., & Embrechts, P.** (2015). "Quantitative Risk Management"

4. **Hull, J.C.** (2018). "Risk Management and Financial Institutions"

5. **Christoffersen, P.F.** (1998). "Evaluating Interval Forecasts"

6. **Kupiec, P.H.** (1995). "Techniques for Verifying the Accuracy of Risk Measurement Models"
