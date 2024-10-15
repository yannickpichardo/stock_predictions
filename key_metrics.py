import streamlit as st


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
