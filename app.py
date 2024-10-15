import streamlit as st
from datetime import date
import yfinance as yf
from prophet import Prophet
import plotly.graph_objects as go
import pandas as pd

# constants
START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")
TRADING_DAYS_CRYPTO = 365
# streamlit page configuration
st.set_page_config(layout="wide", page_title="Crypto Predictions", page_icon="📈")
st.title("Crypto Prediction Dashboard")

# define the stock options
STOCKS = (
    "BTC-USD",
    "ETH-USD",
    "XRP-USD",
    "SOL-USD",
)
# UI comp for user choice of stock
selected_stock = st.selectbox("Select stock", STOCKS)
# Hyperparameter controls for advanced tuning
st.sidebar.header("Advanced Forecasting Settings")
seasonality_mode = st.sidebar.selectbox(
    "Seasonality Mode", ["additive", "multiplicative"]
)
changepoint_scale = st.sidebar.slider("Change Point Prior Scale", 0.01, 0.5, 0.05)
yearly_seasonality = st.sidebar.checkbox("Yearly Seasonality", True)
weekly_seasonality = st.sidebar.checkbox("Weekly Seasonality", True)


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


# Load the dataset
data_load_state = st.text("Loading data...")
data = load_dataset(selected_stock)
if data is not None:
    data_load_state.text("Loading data...completed!")
else:
    st.stop()
df_train = data[["Date", "Close"]].rename(columns={"Date": "ds", "Close": "y"})


# Display the key metrics
def display_key_metrics(data):
    highest_price = data["Close"].max()
    lowest_price = data["Close"].min()
    last_price = data["Close"].iloc[-1]
    prev_price = data["Close"].iloc[-2]
    price_diff = last_price - prev_price
    pct_change = (price_diff / prev_price) * 100
    # Layout for key metrics
    # Layout for centered key metrics
    st.markdown(
        """
        <style>
        .metric-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 20px;
        }
        .metric {
            text-align: center;
            font-size: 20px;
            margin: 0 50px;
        }
        .metric .value {
            font-size: 24px;
            font-style: italic;
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="metric-container">
            <div class="metric">
                <strong>Highest Price</strong><br>
                <span class="value">${highest_price:,.2f}</span>
            </div>
            <div class="metric">
                <strong>Lowest Price</strong><br>
                <span class="value" style="color:red;">${lowest_price:,.2f}</span>
            </div>
            <div class="metric">
                <strong>Change (Last Day)</strong><br>
                <span class="value" style="color:{'green' if price_diff > 0 else 'red'};">
                    {'+' if price_diff > 0 else ''}${price_diff:,.2f} ({pct_change:.2f}%)
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Display key metrics
st.subheader(f"Key Metrics for {selected_stock}")
display_key_metrics(data)


# Function to plot historical candlestick data
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


# Fuction to generate the forecasts
@st.cache_data(ttl=60 * 60)
def get_forecast(
    df_train,
    period,
    seasonality_mode,
    changepoint_scale,
    yearly_seasonality,
    weekly_seasonality,
):
    model = Prophet(
        seasonality_mode=seasonality_mode,
        changepoint_prior_scale=changepoint_scale,
        yearly_seasonality=yearly_seasonality,
        weekly_seasonality=weekly_seasonality,
    )
    model.fit(df_train)
    future = model.make_future_dataframe(periods=period)
    forecast = model.predict(future)
    return forecast, model


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


# Plot forecasted data
plot_forecast(data=data, future_forecast=future_forecast)

st.subheader("Forecast data")
st.write(forecast.tail())
