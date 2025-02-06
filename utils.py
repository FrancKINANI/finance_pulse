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

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate technical indicators without pandas_ta
    """
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Moving Averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()

    # Bollinger Bands
    df['BB_middle'] = df['Close'].rolling(window=20).mean()
    df['BB_upper'] = df['BB_middle'] + 2 * df['Close'].rolling(window=20).std()
    df['BB_lower'] = df['BB_middle'] - 2 * df['Close'].rolling(window=20).std()

    # MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

    return df

def create_price_chart(df: pd.DataFrame, show_indicators: dict = None, dark_mode: bool = True) -> go.Figure:
    """
    Create an interactive price chart with technical indicators
    """
    if show_indicators is None:
        show_indicators = {
            'sma': False,
            'ema': False,
            'bollinger': False,
            'rsi': False,
            'macd': False
        }

    # Calculate indicators
    df = calculate_technical_indicators(df)

    # Create figure with secondary y-axis
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        vertical_spacing=0.05,
                        row_heights=[0.5, 0.25, 0.25])

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

    # Add technical indicators
    if show_indicators['sma']:
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name='SMA 20', line=dict(color='orange')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], name='SMA 50', line=dict(color='blue')), row=1, col=1)

    if show_indicators['ema']:
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], name='EMA 20', line=dict(color='purple')), row=1, col=1)

    if show_indicators['bollinger']:
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], name='BB Upper', line=dict(color='gray', dash='dash')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_middle'], name='BB Middle', line=dict(color='gray')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], name='BB Lower', line=dict(color='gray', dash='dash')), row=1, col=1)

    # Volume chart
    fig.add_trace(
        go.Bar(x=df.index, y=df['Volume'], name='Volume'),
        row=2, col=1
    )

    # RSI
    if show_indicators['rsi']:
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='orange')), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    # MACD
    if show_indicators['macd']:
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='blue')), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], name='Signal', line=dict(color='orange')), row=3, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['MACD_Hist'], name='MACD Histogram'), row=3, col=1)

    # Update layout
    fig.update_layout(
        template='plotly_dark' if dark_mode else 'plotly_white',
        xaxis_rangeslider_visible=False,
        height=800,
        showlegend=True,
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