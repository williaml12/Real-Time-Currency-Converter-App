import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# API_KEY = "5FL7EVZI072LXD2W"
# API_KEY = "HZNR2Y0ODK9MTD1T"
API_KEY = "OQZPNHHQD5N3936K"

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

# ------------------ HISTORICAL FX SUPPORT ------------------
HISTORY_SUPPORTED = {
    "USD", "EUR", "GBP", "JPY", "CHF",
    "CAD", "AUD", "NZD", "SGD", "CNY"
}


# ------------------ SESSION STATE ------------------
if "from_idx" not in st.session_state:
    st.session_state.from_idx = 0
if "to_idx" not in st.session_state:
    st.session_state.to_idx = 3
if "range_days" not in st.session_state:
    st.session_state.range_days = 7

# def swap_currencies():
#     st.session_state.from_currency, st.session_state.to_currency = (
#         st.session_state.to_currency,
#         st.session_state.from_currency,
#     )

def swap_currencies():
    st.session_state.from_currency, st.session_state.to_currency = (
        st.session_state.to_currency,
        st.session_state.from_currency,
    )

def set_range(days):
    st.session_state.range_days = days

# ------------------ AUTO-CONVERSION FUNCTION ------------------
@st.cache_data(ttl=60)
def convert_currency(amount, from_c, to_c):
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
    time_updated = response["Realtime Currency Exchange Rate"]["6. Last Refreshed"]

    return rate * amount, rate, time_updated

# ------------------ INPUTS ------------------
amount = st.number_input("Amount", min_value=0.0, value=1.0, step=0.1)

col1, col2, col3 = st.columns([4, 1, 4])

with col1:
    from_currency = st.selectbox(
        "From Currency",
        currency_keys,
        key="from_currency"
    )


with col2:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    st.button("⇄", on_click=swap_currencies, use_container_width=True)
    # st.button("⇄", on_click=swap_currencies)

with col3:
    to_currency = st.selectbox(
        "To Currency",
        currency_keys,
        key="to_currency"
    )


# Update indices
# st.session_state.from_idx = currency_keys.index(from_currency)
# st.session_state.to_idx = currency_keys.index(to_currency)

from_c = CURRENCIES[from_currency]
to_c = CURRENCIES[to_currency]

# ------------------ AUTO REAL-TIME CONVERSION ------------------
if amount > 0 and from_c != to_c:
    try:
        result, rate, time_updated = convert_currency(amount, from_c, to_c)

        st.success(f"💰 {amount} {from_c} = {result:.2f} {to_c}")
        st.caption(f"Rate: {rate:.6f} | ⏱ Updated: {time_updated}")

    except Exception:
        st.warning("⚠️ Unable to fetch live exchange rate at the moment.")

# ------------------ HISTORICAL DATA ------------------
@st.cache_data(ttl=3600)
def get_fx_history(from_c, to_c):
    url = (
        "https://www.alphavantage.co/query"
        "?function=FX_DAILY"
        f"&from_symbol={from_c}"
        f"&to_symbol={to_c}"
        f"&apikey={API_KEY}"
    )

    response = requests.get(url, timeout=10).json()
    return response.get("Time Series FX (Daily)", {})


# ------------------ ACCURATE 1-YEAR EXCHANGE RATE CHART ------------------
st.markdown("---")
st.subheader("📈 Exchange Rate History (1 Year)")

# @st.cache_data(ttl=3600)
# def get_fx_1y(from_c, to_c):
#     url = (
#         "https://www.alphavantage.co/query"
#         "?function=FX_DAILY"
#         "&outputsize=full"
#         f"&from_symbol={from_c}"
#         f"&to_symbol={to_c}"
#         f"&apikey={API_KEY}"
#     )

#     r = requests.get(url, timeout=10).json()

#     # Guard against throttling / errors
#     if "Time Series FX (Daily)" not in r:
#         return pd.DataFrame()

#     data = r["Time Series FX (Daily)"]

#     df = (
#         pd.DataFrame.from_dict(data, orient="index")
#         .rename(columns={"4. close": "Rate"})
#     )

#     df.index = pd.to_datetime(df.index)
#     df["Rate"] = df["Rate"].astype(float)

#     # ⬅️ TRUE last 1 year (calendar accurate)
#     df = df.sort_index().last("365D")

#     return df

@st.cache_data(ttl=3600)
def get_fx_1y(from_c, to_c):
    url = (
        "https://www.alphavantage.co/query"
        "?function=FX_DAILY"
        "&outputsize=full"
        f"&from_symbol={from_c}"
        f"&to_symbol={to_c}"
        f"&apikey={API_KEY}"
    )

    r = requests.get(url, timeout=10).json()

    # 🚨 Alpha Vantage quota / error handling
    if "Note" in r:
        st.error("🚫 Alpha Vantage API limit reached. Please wait 1 minute.")
        return pd.DataFrame()

    if "Error Message" in r:
        st.error("❌ Invalid API request or API key.")
        return pd.DataFrame()

    if "Time Series FX (Daily)" not in r:
        st.error("⚠️ FX history not returned by API.")
        return pd.DataFrame()

    data = r["Time Series FX (Daily)"]

    df = (
        pd.DataFrame.from_dict(data, orient="index")
        .rename(columns={"4. close": "Rate"})
    )

    df.index = pd.to_datetime(df.index)
    df["Rate"] = df["Rate"].astype(float)

    # ✅ True 1-year slice
    df = df.sort_index().last("365D")

    return df





# df = get_fx_1y(from_c, to_c)

# if not df.empty:
#     fig = px.line(
#         df,
#         x=df.index,
#         y="Rate",
#         title=f"{from_c} → {to_c} | Daily Close (Last 1 Year)",
#         labels={"x": "Date", "Rate": "Exchange Rate"},
#     )

#     fig.update_traces(line=dict(width=2))
#     fig.update_layout(
#         hovermode="x unified",
#         xaxis=dict(showgrid=False),
#         yaxis=dict(showgrid=True),
#         margin=dict(l=40, r=40, t=60, b=40),
#     )

#     st.plotly_chart(fig, use_container_width=True)

#     st.caption(
#         "📌 Data source: Alpha Vantage (Daily FX Close, UTC). "
#         "This chart prioritizes accuracy over intraday estimates."
#     )
# else:
#     st.warning("⚠️ Historical data not available for this currency pair.")


st.markdown("---")
st.subheader("📈 Exchange Rate History (1 Year)")

# Only fetch history if BOTH currencies support it
if from_c in HISTORY_SUPPORTED and to_c in HISTORY_SUPPORTED:

    df = get_fx_1y(from_c, to_c)

    if not df.empty:
        fig = px.line(
            df,
            x=df.index,
            y="Rate",
            title=f"{from_c} → {to_c} | Daily Close (Last 1 Year)",
            labels={"x": "Date", "Rate": "Exchange Rate"},
        )

        fig.update_traces(line=dict(width=2))
        fig.update_layout(
            hovermode="x unified",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True),
            margin=dict(l=40, r=40, t=60, b=40),
        )

        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "📌 Source: Alpha Vantage (Daily FX Close, UTC). "
            "Historical data is limited to major currencies."
        )

    else:
        st.warning("⚠️ Historical data temporarily unavailable.")

else:
    st.info(
        "ℹ️ Exchange rate history is available for major currencies only. "
        "Live conversion still works for this pair."
    )








# import streamlit as st
# import requests
# import pandas as pd
# import plotly.express as px

# API_KEY = "5FL7EVZI072LXD2W"

# st.set_page_config(page_title="Real-Time Currency Converter", page_icon="💱")

# st.title("💱 Real-Time Currency Converter")
# st.caption("Powered by Alpha Vantage API")

# # ------------------ CURRENCY LIST ------------------
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

# # ------------------ SESSION STATE ------------------
# if "from_idx" not in st.session_state:
#     st.session_state.from_idx = 0
# if "to_idx" not in st.session_state:
#     st.session_state.to_idx = 3
# if "range_days" not in st.session_state:
#     st.session_state.range_days = 7  # default = 1W

# def swap_currencies():
#     st.session_state.from_idx, st.session_state.to_idx = (
#         st.session_state.to_idx,
#         st.session_state.from_idx,
#     )

# def set_range(days):
#     st.session_state.range_days = days

# # ------------------ INPUTS ------------------
# amount = st.number_input("Amount", min_value=0.0, value=1.0, step=0.1)

# col1, col2, col3 = st.columns([4, 1, 4])

# with col1:
#     from_currency = st.selectbox(
#         "From Currency",
#         currency_keys,
#         index=st.session_state.from_idx
#     )

# with col2:
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

# # ------------------ REAL-TIME CONVERSION ------------------
# if st.button("Convert 🚀"):
#     try:
#         url = (
#             "https://www.alphavantage.co/query"
#             "?function=CURRENCY_EXCHANGE_RATE"
#             f"&from_currency={from_c}"
#             f"&to_currency={to_c}"
#             f"&apikey={API_KEY}"
#         )

#         response = requests.get(url, timeout=10).json()

#         rate = float(
#             response["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
#         )

#         result = rate * amount
#         time_updated = response["Realtime Currency Exchange Rate"]["6. Last Refreshed"]

#         st.success(f"💰 {amount} {from_c} = {result:.2f} {to_c}")
#         st.caption(f"⏱ Last updated: {time_updated}")

#     except Exception as e:
#         st.error(f"❌ Error: {e}")

# # ------------------ HISTORICAL DATA ------------------
# @st.cache_data(ttl=3600)
# def get_fx_history(from_c, to_c):
#     url = (
#         "https://www.alphavantage.co/query"
#         "?function=FX_DAILY"
#         f"&from_symbol={from_c}"
#         f"&to_symbol={to_c}"
#         f"&apikey={API_KEY}"
#     )
#     response = requests.get(url, timeout=10).json()
#     return response.get("Time Series FX (Daily)", {})

# # ------------------ XE-STYLE CHART ------------------
# st.markdown("---")
# st.subheader("📊 Exchange Rate Chart")

# # ⏱ XE-style time buttons (FIXED)
# b1, b2, b3, b4, b5, b6, b7 = st.columns(7)

# with b1:
#     st.button("1W", key="1w", on_click=set_range, args=(7,))
# with b2:
#     st.button("1M", key="1m", on_click=set_range, args=(30,))
# with b3:
#     st.button("3M", key="3m", on_click=set_range, args=(90,))
# with b4:
#     st.button("1Y", key="1y", on_click=set_range, args=(365,))
# with b5:
#     st.button("2Y", key="2y", on_click=set_range, args=(730,))
# with b6:
#     st.button("5Y", key="5y", on_click=set_range, args=(1825,))
# with b7:
#     st.button("10Y", key="10y", on_click=set_range, args=(3650,))

# range_days = st.session_state.range_days

# history = get_fx_history(from_c, to_c)

# if history:
#     df = (
#         pd.DataFrame(history)
#         .T
#         .rename(columns={"4. close": "Rate"})
#         .astype(float)
#     )

#     df.index = pd.to_datetime(df.index)
#     df = df.sort_index().tail(range_days)

#     if not df.empty:
#         fig = px.line(
#             df,
#             x=df.index,
#             y="Rate",
#             labels={"x": "Date", "Rate": "Exchange Rate"},
#             title=f"{from_c} → {to_c} (Last {range_days} days)"
#         )

#         fig.update_traces(mode="lines")
#         fig.update_layout(
#             hovermode="x unified",
#             xaxis=dict(showgrid=False),
#             yaxis=dict(showgrid=True),
#             margin=dict(l=40, r=40, t=60, b=40)
#         )

#         st.plotly_chart(fig, use_container_width=True)
#     else:
#         st.warning("⚠️ Not enough data for selected range.")
# else:
#     st.warning("⚠️ Historical data not available for this currency pair.")











# import streamlit as st
# import requests
# import pandas as pd
# import plotly.express as px


# API_KEY = "5FL7EVZI072LXD2W"

# st.set_page_config(page_title="Real-Time Currency Converter", page_icon="💱")

# st.title("💱 Real-Time Currency Converter")
# st.caption("Powered by Alpha Vantage API")

# # ------------------ CURRENCY LIST ------------------
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

# # ------------------ SESSION STATE ------------------
# if "from_idx" not in st.session_state:
#     st.session_state.from_idx = 0
# if "to_idx" not in st.session_state:
#     st.session_state.to_idx = 3

# def swap_currencies():
#     st.session_state.from_idx, st.session_state.to_idx = (
#         st.session_state.to_idx,
#         st.session_state.from_idx,
#     )

# # ------------------ INPUTS ------------------
# amount = st.number_input("Amount", min_value=0.0, value=1.0, step=0.1)

# col1, col2, col3 = st.columns([4, 1, 4])

# with col1:
#     from_currency = st.selectbox(
#         "From Currency",
#         currency_keys,
#         index=st.session_state.from_idx
#     )

# with col2:
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

# # ------------------ REAL-TIME CONVERSION ------------------
# if st.button("Convert 🚀"):
#     try:
#         url = (
#             "https://www.alphavantage.co/query"
#             "?function=CURRENCY_EXCHANGE_RATE"
#             f"&from_currency={from_c}"
#             f"&to_currency={to_c}"
#             f"&apikey={API_KEY}"
#         )

#         response = requests.get(url, timeout=10).json()

#         rate = float(
#             response["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
#         )

#         result = rate * amount
#         time_updated = response["Realtime Currency Exchange Rate"]["6. Last Refreshed"]

#         st.success(f"💰 {amount} {from_c} = {result:.2f} {to_c}")
#         st.caption(f"⏱ Last updated: {time_updated}")

#     except Exception as e:
#         st.error(f"❌ Error: {e}")

# # ------------------ HISTORICAL AREA CHART ------------------


# @st.cache_data(ttl=3600)
# def get_fx_history(from_c, to_c):
#     url = (
#         "https://www.alphavantage.co/query"
#         "?function=FX_DAILY"
#         f"&from_symbol={from_c}"
#         f"&to_symbol={to_c}"
#         f"&apikey={API_KEY}"
#     )
#     response = requests.get(url, timeout=10).json()
#     return response.get("Time Series FX (Daily)", {})


# st.markdown("---")
# st.subheader("📊 Exchange Rate Chart (Interactive)")

# # Time range options similar to XE
# chart_range = st.selectbox(
#     "Show chart for:",
#     ["7 Days", "30 Days", "90 Days"],
#     index=1
# )

# range_days = int(chart_range.split()[0])

# history = get_fx_history(from_c, to_c)

# if history:
#     df = (
#         pd.DataFrame(history)
#         .T
#         .rename(columns={"4. close": "Rate"})
#         .astype(float)
#     )

#     df.index = pd.to_datetime(df.index)
#     df = df.sort_index().tail(range_days)

#     if not df.empty:
#         fig = px.line(
#             df,
#             x=df.index,
#             y="Rate",
#             title=f"{from_c} → {to_c} (Last {chart_range})",
#             labels={"x": "Date", "Rate": "Exchange Rate"},
#         )
#         fig.update_traces(mode="lines+markers")
#         fig.update_layout(
#             xaxis=dict(showgrid=False),
#             yaxis=dict(showgrid=True),
#             margin=dict(l=40, r=40, t=60, b=40)
#         )

#         st.plotly_chart(fig, use_container_width=True)
#     else:
#         st.warning("⚠️ Not enough data to plot this range.")
# else:
#     st.warning("⚠️ Historical data not available for this currency pair.")





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
