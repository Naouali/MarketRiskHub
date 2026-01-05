# Contributing to Market Risk Hub

Thank you for your interest in contributing to Market Risk Hub! This document provides guidelines and instructions for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/MarketRiskHub.git
   cd MarketRiskHub
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

## Development Workflow

### 1. Create a Branch

Create a new branch for your feature or bug fix:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

- Follow the existing code style and structure
- Add docstrings to all functions and classes
- Include type hints where appropriate
- Keep functions focused and modular

### 3. Write Tests

All new features should include tests:

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/market_risk_hub
```

### 4. Update Documentation

- Update README.md if adding new features
- Add docstrings following NumPy/Google style
- Create example notebooks if appropriate

### 5. Commit Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add feature: brief description"
```

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear description of changes
- Reference to any related issues
- Screenshots/examples if applicable

## Code Style

### Python Style Guide

- Follow PEP 8 guidelines
- Use meaningful variable names
- Maximum line length: 100 characters
- Use docstrings for all public functions/classes

### Example Docstring

```python
def calculate_var(returns: pd.Series, confidence_level: float = 0.95) -> float:
    """
    Calculate Value at Risk using historical simulation.

    Args:
        returns: Series of historical returns
        confidence_level: Confidence level for VaR (default 0.95)

    Returns:
        VaR value as a positive number

    Raises:
        ValueError: If confidence_level is not between 0 and 1

    Example:
        >>> returns = pd.Series([0.01, -0.02, 0.03])
        >>> var = calculate_var(returns, 0.95)
    """
    # Implementation
```

## Testing Guidelines

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Use descriptive test names
- Test edge cases and error conditions

### Test Structure

```python
import unittest

class TestVaRCalculator(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        # Initialize test data

    def test_feature_name(self):
        """Test specific feature"""
        # Arrange
        # Act
        # Assert
```

## Areas for Contribution

### High Priority

- [ ] Additional risk metrics (Incremental VaR, Marginal VaR)
- [ ] Performance optimizations
- [ ] Extended documentation
- [ ] More example notebooks

### Medium Priority

- [ ] Multi-period VaR
- [ ] Credit risk metrics
- [ ] Risk reporting templates
- [ ] API endpoints

### Low Priority

- [ ] ML-based VaR models
- [ ] Real-time data streaming
- [ ] Additional data sources

## Reporting Issues

When reporting bugs or requesting features:

1. **Check existing issues** to avoid duplicates
2. **Use issue templates** if available
3. **Provide details**:
   - Clear description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Python version and OS
   - Error messages/stack traces

## Code Review Process

1. Maintainers will review pull requests
2. Feedback will be provided for improvements
3. Once approved, changes will be merged
4. Contributors will be acknowledged

## Financial/Quantitative Guidelines

When contributing risk analytics features:

- **Accuracy**: Ensure mathematical correctness
- **Industry standards**: Follow established methodologies
- **References**: Cite academic papers or industry sources
- **Validation**: Include backtests or theoretical validation

## Questions?

Feel free to open an issue for:
- Questions about contributing
- Clarification on design decisions
- Suggestions for improvements

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Market Risk Hub!
