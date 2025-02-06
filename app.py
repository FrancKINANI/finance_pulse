import streamlit as st
import pandas as pd
from utils import get_stock_data, create_price_chart, calculate_metrics, format_large_number
from database import (
    init_db, add_to_watchlist, remove_from_watchlist, 
    get_watchlist, add_search_history, get_recent_searches
)

# Initialize database
init_db()

# Page configuration
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state
if 'ticker_symbol' not in st.session_state:
    st.session_state.ticker_symbol = 'AAPL'
if 'time_period' not in st.session_state:
    st.session_state.time_period = '1y'

# Sidebar
st.sidebar.title('Stock Analysis Dashboard')

# Technical Indicators Section in Sidebar
st.sidebar.subheader("Technical Indicators")
show_indicators = {
    'sma': st.sidebar.checkbox('Show SMA (20, 50)'),
    'ema': st.sidebar.checkbox('Show EMA (20)'),
    'bollinger': st.sidebar.checkbox('Show Bollinger Bands'),
    'rsi': st.sidebar.checkbox('Show RSI'),
    'macd': st.sidebar.checkbox('Show MACD')
}

# Recent Searches
recent_searches = get_recent_searches()
if recent_searches:
    st.sidebar.subheader("Recent Searches")
    for search in recent_searches:
        if st.sidebar.button(f"{search.symbol} ({search.period})", key=f"recent_{search.id}"):
            st.session_state.ticker_symbol = search.symbol
            st.session_state.time_period = search.period
            st.rerun()

# Manual input if no recent searches are selected
ticker_input = st.sidebar.text_input('Enter Stock Symbol', value=st.session_state.ticker_symbol).upper()
time_period = st.sidebar.selectbox(
    'Select Time Period',
    ['1mo', '3mo', '6mo', '1y', '2y', '5y'],
    index=3
)

# Update session state from manual input
st.session_state.ticker_symbol = ticker_input
st.session_state.time_period = time_period

# Watchlist
st.sidebar.subheader("Watchlist")
watchlist = get_watchlist()
for item in watchlist:
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        if st.button(item.symbol, key=f"watchlist_{item.id}"):
            st.session_state.ticker_symbol = item.symbol
            st.rerun()
    with col2:
        if st.button("❌", key=f"remove_{item.id}"):
            remove_from_watchlist(item.symbol)
            st.rerun()

# Main content
if st.session_state.ticker_symbol:
    # Add to search history
    add_search_history(st.session_state.ticker_symbol, st.session_state.time_period)

    # Fetch data
    with st.spinner('Fetching stock data...'):
        hist_data, company_info = get_stock_data(st.session_state.ticker_symbol, st.session_state.time_period)

    if hist_data is not None and company_info is not None:
        # Add to watchlist button
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.title(f"{company_info.get('longName', st.session_state.ticker_symbol)}")
        with col2:
            if st.button("➕ Add to Watchlist"):
                add_to_watchlist(st.session_state.ticker_symbol)
                st.success(f"Added {st.session_state.ticker_symbol} to watchlist!")
        with col3:
            current_price = hist_data['Close'].iloc[-1]
            price_change = current_price - hist_data['Close'].iloc[-2]
            price_change_pct = (price_change / hist_data['Close'].iloc[-2]) * 100
            st.metric(
                "Current Price",
                f"${current_price:.2f}",
                f"{price_change_pct:+.2f}%"
            )

        st.markdown(f"*{company_info.get('sector', 'N/A')} | {company_info.get('industry', 'N/A')}*")

        # Key metrics
        st.subheader('Key Metrics')
        metrics = calculate_metrics(hist_data)
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Market Cap", format_large_number(company_info.get('marketCap', 0)))
        with col2:
            st.metric("P/E Ratio", f"{company_info.get('trailingPE', 0):.2f}")
        with col3:
            st.metric("52W High", f"${company_info.get('fiftyTwoWeekHigh', 0):.2f}")
        with col4:
            st.metric("52W Low", f"${company_info.get('fiftyTwoWeekLow', 0):.2f}")

        # Price chart with technical indicators
        st.subheader('Price Chart')
        fig = create_price_chart(hist_data, show_indicators)
        st.plotly_chart(fig, use_container_width=True)

        # Additional company information
        st.subheader('Company Overview')
        with st.expander("Business Summary"):
            st.write(company_info.get('longBusinessSummary', 'No information available'))

        # Financial metrics table
        st.subheader('Financial Metrics')
        metrics_df = pd.DataFrame({
            'Metric': [
                'Revenue (TTM)',
                'Profit Margin',
                'Operating Margin',
                'Return on Equity',
                'Total Debt',
                'Total Cash'
            ],
            'Value': [
                format_large_number(company_info.get('totalRevenue', 0)),
                f"{company_info.get('profitMargins', 0)*100:.2f}%",
                f"{company_info.get('operatingMargins', 0)*100:.2f}%",
                f"{company_info.get('returnOnEquity', 0)*100:.2f}%",
                format_large_number(company_info.get('totalDebt', 0)),
                format_large_number(company_info.get('totalCash', 0))
            ]
        })
        st.table(metrics_df)

    else:
        st.error(f"Unable to fetch data for {st.session_state.ticker_symbol}. Please check the symbol and try again.")

else:
    st.info("Please enter a stock symbol to begin analysis.")

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    Data provided by Yahoo Finance
</div>
""", unsafe_allow_html=True)