#!/usr/bin/env python
# coding: utf-8

import os
os.system('pip install alpha_vantage streamlit oandapyV20 pandas')  # Install dependencies

import streamlit as st
import pandas as pd
from alpha_vantage.foreignexchange import ForeignExchange
from oandapyV20 import API
import oandapyV20.endpoints.orders as orders
from oandapyV20.contrib.requests import MarketOrderRequest
from config import access_token, accountID, ALPHA_VANTAGE_API_KEY  # Ensure keys are set

# Streamlit UI
st.title("OANDA Forex Trading Bot")
st.sidebar.header("Settings")

# Select currency pair
currency_pairs = {
    "EUR/USD": ("EUR", "USD"),
    "GBP/USD": ("GBP", "USD"),
    "USD/JPY": ("USD", "JPY"),
}

selected_pair = st.sidebar.selectbox("Select Currency Pair", list(currency_pairs.keys()))
from_currency, to_currency = currency_pairs[selected_pair]

# Fetch historical forex data using Alpha Vantage
@st.cache_data(ttl=60)  # Cache data for 60 seconds
def fetch_data(from_currency, to_currency):
    try:
        fx = ForeignExchange(key=ALPHA_VANTAGE_API_KEY)
        data, _ = fx.get_currency_exchange_intraday(from_currency, to_currency, interval='5min', outputsize='compact')
        df = pd.DataFrame(data).T  # Transpose to match previous format
        df.columns = ["Open", "High", "Low", "Close"]
        df = df.astype(float)
        df.index = pd.to_datetime(df.index)  # Convert index to datetime
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

data = fetch_data(from_currency, to_currency)

if not data.empty:
    st.subheader(f"Latest Data for {selected_pair}")
    st.write(data.tail(5))

    # Signal Generator
    def signal_generator(df):
        if len(df) < 2:
            return "No Data"
        open_price, close_price = df.Open.iloc[-1], df.Close.iloc[-1]
        prev_open, prev_close = df.Open.iloc[-2], df.Close.iloc[-2]

        if open_price > close_price and prev_open < prev_close and close_price < prev_open:
            return "Sell"
        elif open_price < close_price and prev_open > prev_close and close_price > prev_open:
            return "Buy"
        return "Hold"

    signal = signal_generator(data)
    st.subheader(f"Trading Signal: {signal}")

    # Place Trade
    def place_trade(signal):
        if signal == "Hold":
            st.warning("No trade signal")
            return

        client = API(access_token)
        units = 1000 if signal == "Buy" else -1000
        order = MarketOrderRequest(instrument=f"{from_currency}_{to_currency}", units=units)
        r = orders.OrderCreate(accountID, data=order.data)
        response = client.request(r)
        st.success(f"Trade Executed: {response}")

    if st.button("Execute Trade"):
        place_trade(signal)
else:
    st.warning("No data available.")
