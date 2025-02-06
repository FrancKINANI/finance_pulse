import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def get_stock_data(ticker_symbol: str, period: str = "1y") -> tuple:
    """
    Fetch stock data and company info from Yahoo Finance
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period=period)
        info = ticker.info
        return hist, info
    except Exception as e:
        return None, None

def create_price_chart(df: pd.DataFrame, dark_mode: bool = True) -> go.Figure:
    """
    Create an interactive price chart with volume
    """
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, 
                        row_heights=[0.7, 0.3])

    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC'
        ),
        row=1, col=1
    )

    # Volume chart
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume'
        ),
        row=2, col=1
    )

    fig.update_layout(
        template='plotly_dark' if dark_mode else 'plotly_white',
        xaxis_rangeslider_visible=False,
        height=600,
        showlegend=False,
        margin=dict(l=0, r=0, t=30, b=0)
    )

    return fig

def calculate_metrics(df: pd.DataFrame) -> dict:
    """
    Calculate key financial metrics
    """
    metrics = {
        'Daily Returns': df['Close'].pct_change().mean() * 100,
        'Volatility': df['Close'].pct_change().std() * 100,
        'Highest Price': df['High'].max(),
        'Lowest Price': df['Low'].min(),
        'Average Volume': df['Volume'].mean()
    }
    return metrics

def format_large_number(num: float) -> str:
    """
    Format large numbers for display
    """
    if num >= 1e9:
        return f"{num/1e9:.2f}B"
    elif num >= 1e6:
        return f"{num/1e6:.2f}M"
    elif num >= 1e3:
        return f"{num/1e3:.2f}K"
    return f"{num:.2f}"
