import streamlit as st
from datetime import date
import yfinance as yf
from prophet import Prophet
import plotly.graph_objects as go
import pandas as pd

START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")
TRADING_DAYS_CRYPTO = 365

st.set_page_config(layout="wide", page_title="Crypto Predictions", page_icon="📈")
st.title("Crypto Prediction Dashboard")


STOCKS = (
    "BTC-USD",
    "ETH-USD",
    "XRP-USD",
    "SOL-USD",
)
selected_stock = st.selectbox("Select stock", STOCKS)


@st.cache_data(ttl=60 * 60)  # 1 hour cache
def load_dataset(ticker):
    try:
        data = yf.download(ticker, START, TODAY)
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return None


data_load_state = st.text("Loading data...")
data = load_dataset(selected_stock)
if data is not None:
    data_load_state.text("Loading data...completed!")
else:
    st.stop()
df_train = data[["Date", "Close"]].rename(columns={"Date": "ds", "Close": "y"})


@st.cache_data(ttl=60 * 60)
def get_forecast(df_train, period):
    model = Prophet()
    model.fit(df_train)
    future = model.make_future_dataframe(periods=period)
    forecast = model.predict(future)
    return forecast, model


# Forecasting logic
n_years = st.slider("Years of prediction:", 1, 5)
period = n_years * TRADING_DAYS_CRYPTO
forecast, model = get_forecast(df_train, period)
future_forecast = forecast[forecast["ds"] > pd.Timestamp.now()]


def plot_forecast(data, future_forecast):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["Close"],
            name="Historical Data",
            line=dict(color="gray"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=future_forecast["ds"],
            y=future_forecast["yhat"],
            mode="lines",
            name="Future Predictions",
            line=dict(color="blue"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=future_forecast["ds"],
            y=future_forecast["yhat_upper"],
            mode="lines",
            name="Upper Bound",
            line=dict(color="lightblue"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=future_forecast["ds"],
            y=future_forecast["yhat_lower"],
            mode="lines",
            name="Lower Bound",
            line=dict(color="lightblue"),
            fill="tonexty",
        )
    )
    fig.layout.update(
        title_text="Forecast Time Series",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        xaxis_rangeslider_visible=True,
        template="plotly_dark",
        autosize=True,
    )
    st.plotly_chart(fig, use_container_width=True)


plot_forecast(data=data, future_forecast=future_forecast)
st.subheader("Forecast data")
st.write(forecast.tail())


def plot_raw_data():
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=data["Date"],
                open=data["Open"],
                high=data["High"],
                low=data["Low"],
                close=data["Close"],
                name="Candlesticks",
            )
        ]
    )
    fig.layout.update(
        title_text="Historical Price Data (Candlesticks)",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_dark",
        xaxis_rangeslider_visible=True,
        autosize=True,
        hovermode="x",
    )
    st.plotly_chart(fig)


plot_raw_data()
st.subheader("Raw data")
st.write(data.tail())
