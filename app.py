import streamlit as st
import requests

API_KEY = "5FL7EVZI072LXD2W"

st.set_page_config(page_title="Real-Time Currency Converter", page_icon="💱")

st.title("💱 Real-Time Currency Converter")
st.caption("Powered by Alpha Vantage API")

# ---- User Inputs ----
amount = st.number_input("Amount", min_value=0.0, value=1.0, step=0.1)

col1, col2 = st.columns(2)
with col1:
    from_c = st.text_input("From Currency (e.g., USD)", "USD")
with col2:
    to_c = st.text_input("To Currency (e.g., INR)", "INR")

# ---- Convert Button ----
if st.button("Convert 🚀"):
    try:
        url = (
            "https://www.alphavantage.co/query"
            "?function=CURRENCY_EXCHANGE_RATE"
            f"&from_currency={from_c}"
            f"&to_currency={to_c}"
            f"&apikey={API_KEY}"
        )

        response = requests.get(url).json()

        rate = float(
            response["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
        )

        result = rate * amount

        from_name = response["Realtime Currency Exchange Rate"]["2. From_Currency Name"]
        to_name = response["Realtime Currency Exchange Rate"]["4. To_Currency Name"]
        time = response["Realtime Currency Exchange Rate"]["6. Last Refreshed"]

        st.success(f"💰 {amount} {from_c.upper()} = {result:.2f} {to_c.upper()}")

        st.markdown("### 📊 Exchange Details")
        st.write(f"**From:** {from_name}")
        st.write(f"**To:** {to_name}")
        st.write(f"**Rate:** {rate}")
        st.write(f"**Last Updated:** {time}")

    except Exception as e:
        st.error(f"❌ Error: {e}")
