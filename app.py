import streamlit as st
from datetime import date
import yfinance as yf
from prophet import Prophet
import plotly.graph_objects as go
from prophet.plot import plot_plotly

START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")
TRADING_DAYS_CRYPTO = 365
st.title("Crypto Prediction Dashboard")

stocks = (
    "BTC-USD",
    "ETH-USD",
    "XRP-USD",
    "SOL-USD",
)
selected_stock = st.selectbox("Select stock", stocks)


@st.cache_data
def load_dataset(ticker):
    data = yf.download(ticker, START, TODAY)
    data.reset_index(inplace=True)
    return data


data_load_state = st.text("Loading data...")
data = load_dataset(selected_stock)
data_load_state.text("Loading data...completed!")
n_years = st.slider("Years of prediction:", 1, 5)
period = n_years * TRADING_DAYS_CRYPTO

df_train = data[["Date", "Close"]]
df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})
model = Prophet()
model.fit(df_train)
future = model.make_future_dataframe(periods=period)
forecast = model.predict(future)

st.subheader("Forecast data")
st.write(forecast.tail())
st.write("Forecast Timeseries")
fig1 = plot_plotly(model, forecast)
st.plotly_chart(fig1)

st.subheader("Raw data")
st.write(data.tail())


def plot_raw_data():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data["Date"], y=data["Open"], name="stock_open"))
    fig.add_trace(go.Scatter(x=data["Date"], y=data["Close"], name="stock_close"))
    fig.layout.update(title_text="Time Series data", xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)


plot_raw_data()
