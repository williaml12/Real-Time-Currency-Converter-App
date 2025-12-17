import streamlit as st
import requests
import pandas as pd

API_KEY = "5FL7EVZI072LXD2W"

st.set_page_config(page_title="Real-Time Currency Converter", page_icon="💱")

st.title("💱 Real-Time Currency Converter")
st.caption("Powered by Alpha Vantage API")

# ------------------ CURRENCY LIST ------------------
CURRENCIES = {
    "USD – US Dollar": "USD",
    "EUR – Euro": "EUR",
    "GBP – British Pound": "GBP",
    "INR – Indian Rupee": "INR",
    "JPY – Japanese Yen": "JPY",
    "AUD – Australian Dollar": "AUD",
    "CAD – Canadian Dollar": "CAD",
    "CHF – Swiss Franc": "CHF",
    "CNY – Chinese Yuan": "CNY",
    "SGD – Singapore Dollar": "SGD",
    "NZD – New Zealand Dollar": "NZD",
    "ZAR – South African Rand": "ZAR",
    "AED – UAE Dirham": "AED",
    "SAR – Saudi Riyal": "SAR",
    "MYR – Malaysian Ringgit": "MYR",
    "THB – Thai Baht": "THB"
}

currency_keys = list(CURRENCIES.keys())

# ------------------ SESSION STATE ------------------
if "from_idx" not in st.session_state:
    st.session_state.from_idx = 0
if "to_idx" not in st.session_state:
    st.session_state.to_idx = 3

def swap_currencies():
    st.session_state.from_idx, st.session_state.to_idx = (
        st.session_state.to_idx,
        st.session_state.from_idx,
    )

# ------------------ INPUTS ------------------
amount = st.number_input("Amount", min_value=0.0, value=1.0, step=0.1)

col1, col2, col3 = st.columns([4, 1, 4])

with col1:
    from_currency = st.selectbox(
        "From Currency",
        currency_keys,
        index=st.session_state.from_idx
    )

with col2:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    st.button("⇄", on_click=swap_currencies)

with col3:
    to_currency = st.selectbox(
        "To Currency",
        currency_keys,
        index=st.session_state.to_idx
    )

# Update indices
st.session_state.from_idx = currency_keys.index(from_currency)
st.session_state.to_idx = currency_keys.index(to_currency)

from_c = CURRENCIES[from_currency]
to_c = CURRENCIES[to_currency]

# ------------------ REAL-TIME CONVERSION ------------------
if st.button("Convert 🚀"):
    try:
        url = (
            "https://www.alphavantage.co/query"
            "?function=CURRENCY_EXCHANGE_RATE"
            f"&from_currency={from_c}"
            f"&to_currency={to_c}"
            f"&apikey={API_KEY}"
        )

        response = requests.get(url, timeout=10).json()

        rate = float(
            response["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
        )

        result = rate * amount
        time_updated = response["Realtime Currency Exchange Rate"]["6. Last Refreshed"]

        st.success(f"💰 {amount} {from_c} = {result:.2f} {to_c}")
        st.caption(f"⏱ Last updated: {time_updated}")

    except Exception as e:
        st.error(f"❌ Error: {e}")

# ------------------ HISTORICAL AREA CHART ------------------
st.markdown("---")
st.subheader("📉 Exchange Rate Chart")

days = st.selectbox(
    "Select time range",
    options=[7, 30, 90],
    index=1
)

history = get_fx_history(from_c, to_c)

if history:
    df = (
        pd.DataFrame(history)
        .T
        .rename(columns={"4. close": "Rate"})
        .astype(float)
    )

    df.index = pd.to_datetime(df.index)
    df = df.sort_index().tail(days)

    st.line_chart(df["Rate"], height=300)

    st.caption(f"{from_c} → {to_c} exchange rate over the last {days} days")
else:
    st.warning("⚠️ Historical exchange rate data not available.")






# import streamlit as st
# import requests

# API_KEY = "5FL7EVZI072LXD2W"

# st.set_page_config(page_title="Real-Time Currency Converter", page_icon="💱")

# st.title("💱 Real-Time Currency Converter")
# st.caption("Powered by Alpha Vantage API")

# CURRENCIES = {
#     "USD – US Dollar": "USD",
#     "EUR – Euro": "EUR",
#     "GBP – British Pound": "GBP",
#     "INR – Indian Rupee": "INR",
#     "JPY – Japanese Yen": "JPY",
#     "AUD – Australian Dollar": "AUD",
#     "CAD – Canadian Dollar": "CAD",
#     "CHF – Swiss Franc": "CHF",
#     "CNY – Chinese Yuan": "CNY",
#     "SGD – Singapore Dollar": "SGD",
#     "NZD – New Zealand Dollar": "NZD",
#     "ZAR – South African Rand": "ZAR",
#     "AED – UAE Dirham": "AED",
#     "SAR – Saudi Riyal": "SAR",
#     "MYR – Malaysian Ringgit": "MYR",
#     "THB – Thai Baht": "THB"
# }

# currency_keys = list(CURRENCIES.keys())

# if "from_idx" not in st.session_state:
#     st.session_state.from_idx = 0
# if "to_idx" not in st.session_state:
#     st.session_state.to_idx = 3

# def swap_currencies():
#     st.session_state.from_idx, st.session_state.to_idx = (
#         st.session_state.to_idx,
#         st.session_state.from_idx,
#     )

# amount = st.number_input("Amount", min_value=0.0, value=1.0, step=0.1)

# col1, col2, col3 = st.columns([4, 1, 4])

# with col1:
#     from_currency = st.selectbox(
#         "From Currency",
#         currency_keys,
#         index=st.session_state.from_idx
#     )

# with col2:
#     # st.markdown("<br>", unsafe_allow_html=True)
#     st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
#     st.button("⇄", on_click=swap_currencies)

# with col3:
#     to_currency = st.selectbox(
#         "To Currency",
#         currency_keys,
#         index=st.session_state.to_idx
#     )

# # Update indices
# st.session_state.from_idx = currency_keys.index(from_currency)
# st.session_state.to_idx = currency_keys.index(to_currency)

# from_c = CURRENCIES[from_currency]
# to_c = CURRENCIES[to_currency]

# if st.button("Convert 🚀"):
#     try:
#         url = (
#             "https://www.alphavantage.co/query"
#             "?function=CURRENCY_EXCHANGE_RATE"
#             f"&from_currency={from_c}"
#             f"&to_currency={to_c}"
#             f"&apikey={API_KEY}"
#         )

#         response = requests.get(url).json()
#         rate = float(
#             response["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
#         )

#         result = rate * amount
#         time = response["Realtime Currency Exchange Rate"]["6. Last Refreshed"]

#         st.success(f"💰 {amount} {from_c} = {result:.2f} {to_c}")
#         st.caption(f"⏱ Last updated: {time}")

#     except Exception as e:
#         st.error(f"❌ Error: {e}")









# import streamlit as st
# import requests

# API_KEY = "5FL7EVZI072LXD2W"

# st.set_page_config(page_title="Real-Time Currency Converter", page_icon="💱")

# st.title("💱 Real-Time Currency Converter")
# st.caption("Powered by Alpha Vantage API")

# # ---- User Inputs ----
# amount = st.number_input("Amount", min_value=0.0, value=1.0, step=0.1)

# col1, col2 = st.columns(2)
# with col1:
#     from_c = st.text_input("From Currency (e.g., USD)", "USD")
# with col2:
#     to_c = st.text_input("To Currency (e.g., INR)", "INR")

# # ---- Convert Button ----
# if st.button("Convert 🚀"):
#     try:
#         url = (
#             "https://www.alphavantage.co/query"
#             "?function=CURRENCY_EXCHANGE_RATE"
#             f"&from_currency={from_c}"
#             f"&to_currency={to_c}"
#             f"&apikey={API_KEY}"
#         )

#         response = requests.get(url).json()

#         rate = float(
#             response["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
#         )

#         result = rate * amount

#         from_name = response["Realtime Currency Exchange Rate"]["2. From_Currency Name"]
#         to_name = response["Realtime Currency Exchange Rate"]["4. To_Currency Name"]
#         time = response["Realtime Currency Exchange Rate"]["6. Last Refreshed"]

#         st.success(f"💰 {amount} {from_c.upper()} = {result:.2f} {to_c.upper()}")

#         st.markdown("### 📊 Exchange Details")
#         st.write(f"**From:** {from_name}")
#         st.write(f"**To:** {to_name}")
#         st.write(f"**Rate:** {rate}")
#         st.write(f"**Last Updated:** {time}")

#     except Exception as e:
#         st.error(f"❌ Error: {e}")
