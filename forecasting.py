import streamlit as st
from prophet import Prophet


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
