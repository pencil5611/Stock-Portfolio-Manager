import yfinance as yf
import pandas as pd
import numpy as np


def download_data(ticker, benchmark='SPY', period='1y'):
    stock_df = yf.download(ticker, period=period, auto_adjust=True)
    market_df = yf.download(benchmark, period=period, auto_adjust=True)

    return stock_df['Close'].dropna(), market_df['Close'].dropna()

def compute_daily_returns(prices):
    return prices.pct_change().dropna()

def calculate_volatility(returns):
    return np.std(returns) * np.sqrt(252)

def calculate_beta(stock_returns, market_returns):
    aligned = pd.concat([stock_returns, market_returns], axis=1).dropna()
    return np.cov(aligned.iloc[:, 0], aligned.iloc[:, 1])[0][1] / np.var(aligned.iloc[:, 1])


def calculate_max_drawdown(prices):
    cumulative = (1 + prices.pct_change()).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    return drawdown.min()

def calculate_sharpe_ratio(returns, risk_free_rate=0.01):
    excess = returns - (risk_free_rate / 252)
    return (excess.mean() / excess.std()) * np.sqrt(252)

def calculate_var(returns, confidence=0.95):
    return np.percentile(returns, (1 - confidence) * 100)