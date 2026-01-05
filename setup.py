from setuptools import setup, find_packages

setup(
    name="market-risk-hub",
    version="1.0.0",
    description="Comprehensive Market Risk Analytics Engine",
    author="Noual Inabil",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "yfinance>=0.2.35",
        "pandas>=2.1.4",
        "numpy>=1.26.2",
        "scipy>=1.11.4",
        "statsmodels>=0.14.1",
        "plotly>=5.18.0",
        "matplotlib>=3.8.2",
        "seaborn>=0.13.0",
        "streamlit>=1.29.0",
    ],
)
