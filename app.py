import streamlit as st
from sidebar_options import Portfolio_Manager, Risk_Analysis, Transaction_History, Ticker_Watchlist, Stock_Research

st.sidebar.title('Navigation')
page = st.sidebar.selectbox('Select Page', ['Portfolio Manager', 'Risk Analysis', 'Transaction History', 'Watchlist', 'Research'])

if page == 'Portfolio Manager':
    try:
        Portfolio_Manager.show()
    except KeyError:
        st.error('Key Error: Invalid Ticker Symbol')

if page == 'Risk Analysis':
    try:
        Risk_Analysis.show()
    except KeyError:
        st.error('Key Error: Invalid Ticker Symbol')


if page == 'Transaction History':
    try:
        Transaction_History.show()
    except KeyError:
        st.error('Key Error: Invalid Ticker Symbol')

if page == 'Watchlist':
    try:
        Ticker_Watchlist.show()
    except KeyError:
        st.error('Key Error: Invalid Ticker Symbol')

if page == 'Research':
    try:
        Stock_Research.show()
    except KeyError:
        st.error('Key Error: Invalid Ticker Symbol')
