import yfinance as yf
import streamlit as st

# Constants
from constants import START, TODAY


# Get the data from Yahoo Finance
@st.cache_data(ttl=60 * 60)  # 1 hour cache
def load_dataset(ticker):
    try:
        data = yf.download(ticker, START, TODAY)
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return None
