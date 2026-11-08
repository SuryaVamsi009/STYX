# STYX Instructions

## Overview
STYX (Systematic Trader's Yield eXtractor) is a research and paper-trading pipeline for Indian equities.

## Project Structure
```
STYX/
├── src/
│   ├── styx/              # Main package
│   │   ├── __init__.py
│   │   ├── data/          # Data fetching modules
│   │   │   ├── __init__.py
│   │   │   ├── nsepy.py   # NSE data fetcher
│   │   │   └── alphavantage.py  # Alpha Vantage integration
│   │   ├── strategies/    # Trading strategies
│   │   │   ├── __init__.py
│   │   │   ├── momentum.py
│   │   │   └── mean_reversion.py
│   │   ├── backtest/      # Backtesting engine
│   │   │   ├── __init__.py
│   │   │   └── engine.py
│   │   ├── paper_trading/ # Paper trading module
│   │   │   ├── __init__.py
│   │   │   ├── executor.py
│   │   │   └── broker.py
│   │   └── utils/         # Utility functions
│   │       ├── __init__.py
│   │       └── validators.py
├── tests/                 # Test suite
├── notebooks/             # Jupyter notebooks for research
├── data/                  # Local data storage
├── config.yaml            # Strategy configuration
├── .env                   # Environment variables (API keys)
├── requirements.txt       # Python dependencies
├── README.md
└── instructions.md
```

## Setup
1. Clone the repository
2. Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Set up API keys in `.env` file
5. Configure strategy parameters in `config.yaml`

## Usage
- Research mode: `python -m src.styx.data.nsepy`
- Backtesting: `python -m src.styx.backtest.engine`
- Paper trading: `python -m src.styx.paper_trading.executor`

## Contributing
- Follow the coding standards
- Submit pull requests for review
- Ensure all tests pass before merging
- Add new strategies in `src/styx/strategies/`

## Configuration
- Edit `.env` file for API keys (NSE, Alpha Vantage, etc.)
- Update `config.yaml` for strategy parameters (risk limits, capital, etc.)
- Review `src/styx/utils/validators.py` for data validation rules