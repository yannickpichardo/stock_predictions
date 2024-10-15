import streamlit as st
import plotly.graph_objects as go


def plot_candlestick_data(data):
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
