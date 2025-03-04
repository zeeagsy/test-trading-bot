#!/usr/bin/env python
# coding: utf-8

# In[3]:

import os
os.system('pip install yfinance')
import yfinance as yf
import streamlit as st
import pandas as pd
from oandapyV20 import API
import oandapyV20.endpoints.orders as orders
from oandapyV20.contrib.requests import MarketOrderRequest, TakeProfitDetails, StopLossDetails
from config import access_token, accountID  # Ensure this is correctly set up

# Streamlit UI
st.title("OANDA Forex Trading Bot")
st.sidebar.header("Settings")

# Select currency pair
currency_pair = st.sidebar.selectbox("Select Currency Pair", ["EURUSD=X", "GBPUSD=X", "USDJPY=X"])
interval = st.sidebar.selectbox("Select Time Interval", ["1m", "5m", "15m"])

# Fetch historical data
@st.cache_data(ttl=60)  # Cache data for 60 seconds
def fetch_data(pair, interval):
    try:
        data = yf.download(pair, start="2022-1-5", end="2025-1-7", interval=interval)
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

data = fetch_data(currency_pair, interval)

if not data.empty:
    st.subheader(f"Latest Data for {currency_pair}")
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
        order = MarketOrderRequest(instrument="EUR_USD", units=units)
        r = orders.OrderCreate(accountID, data=order.data)
        response = client.request(r)
        st.success(f"Trade Executed: {response}")

    if st.button("Execute Trade"):
        place_trade(signal)
else:
    st.warning("No data available.")



# In[ ]:





# In[ ]:




