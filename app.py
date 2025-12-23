import streamlit as st
import requests
import pandas as pd
import plotly.express as px


API_KEY = st.secrets["CURRENCY_API_KEY"]


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
# if "from_idx" not in st.session_state:
#     st.session_state.from_idx = 0
# if "to_idx" not in st.session_state:
#     st.session_state.to_idx = 3
# if "range_days" not in st.session_state:
#     st.session_state.range_days = 7  # default = 1W

if "from_currency" not in st.session_state:
    st.session_state.from_currency = currency_keys[0]

if "to_currency" not in st.session_state:
    st.session_state.to_currency = currency_keys[3]


def swap_currencies():
    st.session_state.from_currency, st.session_state.to_currency = (
        st.session_state.to_currency,
        st.session_state.from_currency,
    )


# def set_range(days):
#     st.session_state.range_days = days

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
st.session_state.from_idx = currency_keys.index(from_currency)
st.session_state.to_idx = currency_keys.index(to_currency)

from_c = CURRENCIES[st.session_state.from_currency]
to_c = CURRENCIES[st.session_state.to_currency]

# ------------------ REAL-TIME CONVERSION ------------------
st.markdown("")  # small spacing

c1, c2, c3 = st.columns([3, 2, 3])

with c2:
    convert_clicked = st.button("Convert 🚀", use_container_width=True)

if convert_clicked:
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
        # st.caption(f"⏱ Last updated: {time_updated}")
        st.caption(f"Rate: {rate:.6f} | ⏱ Updated: {time_updated}")

    except Exception as e:
        st.error(f"❌ Error: {e}")

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

# ------------------ 6-MONTH EXCHANGE RATE CHART ------------------
st.markdown("---")
st.subheader("📈 Exchange Rate History (Last 6 Months)")

@st.cache_data(ttl=3600)
def get_fx_6m(from_c, to_c):
    url = (
        "https://www.alphavantage.co/query"
        "?function=FX_DAILY"
        "&outputsize=full"
        f"&from_symbol={from_c}"
        f"&to_symbol={to_c}"
        f"&apikey={API_KEY}"
    )
    r = requests.get(url, timeout=10).json()

    if "Time Series FX (Daily)" not in r:
        return pd.DataFrame()

    df = (
        pd.DataFrame(r["Time Series FX (Daily)"])
        .T
        .rename(columns={"4. close": "Rate"})
        .astype(float)
    )

    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    # ✅ TRUE last 6 months
    end_date = df.index.max()
    start_date = end_date - pd.DateOffset(months=6)
    df = df.loc[df.index >= start_date]

    return df


df = get_fx_6m(from_c, to_c)

if not df.empty:
    fig = px.line(
        df,
        x=df.index,
        y="Rate",
        title=f"{from_c} → {to_c} (Last 6 Months)",
        labels={"x": "Date", "Rate": "Exchange Rate"},
    )

    fig.update_layout(
        hovermode="x unified",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True),
        margin=dict(l=40, r=40, t=60, b=40),
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption("📌 Data source: Alpha Vantage (Daily FX Close)")
else:
    st.warning("⚠️ Historical data not available for this currency pair.")









