import pandas as pd
import streamlit as st

from constants import STOCKS, TRADING_DAYS_CRYPTO
from forecasting import get_forecast
from graphing import plot_candlestick_data, plot_forecast
from yahoo import load_dataset

# streamlit page configuration
st.set_page_config(layout="wide", page_title="Crypto Predictions", page_icon="📈")
st.title("Crypto Prediction Dashboard")

# UI comp for user choice of stock
selected_stock = st.selectbox("Select stock", STOCKS)
# Hyperparameter controls for advanced tuning
st.sidebar.header("Advanced Forecasting Settings")
seasonality_mode = st.sidebar.selectbox(
    "Seasonality Mode", ["multiplicative", "additive"]
)
changepoint_scale = st.sidebar.slider("Change Point Prior Scale", 0.01, 0.5, 0.20)
yearly_seasonality = st.sidebar.checkbox("Yearly Seasonality", True)
weekly_seasonality = st.sidebar.checkbox("Weekly Seasonality", True)


# Load the dataset
data_load_state = st.success("Loading data...")
data = load_dataset(selected_stock)
if data is not None:
    data_load_state.success("Loading data...completed!")
else:
    st.stop()

df_train = data[["Date", "Close"]].rename(columns={"Date": "ds", "Close": "y"})


# Display key metrics
st.subheader(f"Key Metrics for {selected_stock}")
# display_key_metrics(data)
col1, col2, col3 = st.columns(3)
col1.metric(
    "Current Price",
    f"${data['Close'].iloc[-1]:,.2f}",
    delta=f"{data['Close'].iloc[-1] - data['Close'].iloc[-2]}",
)
col2.metric("Highest Price", f"${data['Close'].max():,.2f}")
col3.metric("Lowest Price", f"${data['Close'].min():,.2f}")


# Function to plot historical candlestick data
plot_candlestick_data(data)
st.subheader("Raw data")
st.write(data.tail())

# Forecasting logic
n_years = st.slider("Years of prediction:", 1, 5)
period = n_years * TRADING_DAYS_CRYPTO
advanced_settings = (
    seasonality_mode,
    changepoint_scale,
    yearly_seasonality,
    weekly_seasonality,
)
forecast, model = get_forecast(df_train, period, *advanced_settings)
future_data = forecast[forecast["ds"] > pd.Timestamp.now()]

# Plot forecasted data
plot_forecast(data=data, future_forecast=future_data)
st.subheader("Forecast data")
st.write(forecast.tail())
