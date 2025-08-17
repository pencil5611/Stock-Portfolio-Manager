import streamlit as st
import pandas as pd
import yfinance as yf
import os
from dotenv import load_dotenv
from groq import Groq
import plotly.express as px
from datetime import datetime, timedelta
load_dotenv()

API_KEY = os.getenv("API_KEY")
CSV_FILE = 'portfolio.csv'
CASH_FILE = 'cash.csv'
LAST_REFRESH_FILE = 'last_refresh.txt'
TRANSACTIONS_FILE = 'transactions.csv'

def render_portfolio_manager():
    client = Groq(api_key=API_KEY)

    def log_transaction(date, txn_type, ticker, shares, price_per_share, total_value, notes=""):
        # Append to CSV
        new_row = {
            "Date": date,
            "Type": txn_type,  # "Buy" / "Sell"
            "Ticker": ticker,
            "Shares": shares,
            "Price Per Share": price_per_share,
            "Total Value": total_value,
            "Notes": notes
        }
        df = pd.DataFrame([new_row])
        df.to_csv(TRANSACTIONS_FILE, mode="a", header=not os.path.exists(TRANSACTIONS_FILE), index=False)


    # Helper functions for cash
    def load_cash():
        if os.path.exists(CASH_FILE):
            df_cash = pd.read_csv(CASH_FILE)
            if not df_cash.empty and 'Cash' in df_cash.columns:
                return float(df_cash.at[0, 'Cash'])
        return 0.0

    def save_cash(cash_amount):
        df_cash = pd.DataFrame({'Cash': [cash_amount]})
        df_cash.to_csv(CASH_FILE, index=False)

    # Helper functions for last refresh timestamp
    def load_last_refresh():
        if os.path.exists(LAST_REFRESH_FILE):
            with open(LAST_REFRESH_FILE, 'r') as f:
                ts_str = f.read().strip()
                try:
                    return datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
                except:
                    return None
        return None

    def save_last_refresh(dt):
        with open(LAST_REFRESH_FILE, 'w') as f:
            f.write(dt.strftime('%Y-%m-%d %H:%M:%S'))

    # Load portfolio and cash
    if 'portfolio_df' not in st.session_state:
        if os.path.exists(CSV_FILE):
            st.session_state.portfolio_df = pd.read_csv(CSV_FILE)
        else:
            st.session_state.portfolio_df = pd.DataFrame(
                columns=[
                    'Ticker',
                    'Shares',
                    'Share Price ($)',
                    'Total Value ($)',
                    'Price Change Per Share ($)',
                    'Total Change ($)'
                ]
            )

    if 'cash' not in st.session_state:
        st.session_state.cash = load_cash()

    if 'sector_data' not in st.session_state:
        st.session_state.sector_data = {}

    # Initialize last_refresh if not set
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = load_last_refresh()

    st.title("📈 Portfolio Manager")

    # Cash input
    cash_input = st.number_input(
        "Cash Assets ($)",
        min_value=0.0,
        step=0.01,
        format="%.2f",
        value=st.session_state.cash
    )
    if cash_input != st.session_state.cash:
        st.session_state.cash = cash_input
        save_cash(cash_input)

    # Stock add/remove form
    with st.form("stock_form", clear_on_submit=True):
        ticker = st.text_input("Ticker Symbol").upper()
        shares = st.number_input("Shares", min_value=0.0, step=0.0001, format="%.4f")
        notes = st.text_input("Notes")
        submitted_add = st.form_submit_button("Add Stock / Shares")
        submitted_remove = st.form_submit_button("Remove Stock / Shares")

        if submitted_add:
            if ticker == "":
                st.warning("Please enter a ticker symbol.")
            else:
                yfinance_ticker = yf.Ticker(ticker)
                share_price = yfinance_ticker.info.get('regularMarketPrice')
                previous_close = yfinance_ticker.info.get('previousClose')

                if share_price is None or previous_close is None:
                    st.warning(f"Could not fetch price data for {ticker}. Try again later.")
                else:
                    price_change_per_share = share_price - previous_close
                    total_price = share_price * float(shares)
                    total_change = price_change_per_share * float(shares)

                    df = st.session_state.portfolio_df
                    if ticker in df['Ticker'].values:
                        idx = df.index[df['Ticker'] == ticker][0]
                        df.at[idx, 'Shares'] += shares
                        df.at[idx, 'Share Price ($)'] = share_price
                        df.at[idx, 'Total Value ($)'] = df.at[idx, 'Shares'] * share_price
                        df.at[idx, 'Price Change Per Share ($)'] = price_change_per_share
                        df.at[idx, 'Total Change ($)'] = price_change_per_share * df.at[idx, 'Shares']
                    else:
                        new_row = pd.DataFrame({
                            'Ticker': [ticker],
                            'Shares': [shares],
                            'Share Price ($)': [share_price],
                            'Total Value ($)': [total_price],
                            'Price Change Per Share ($)': [price_change_per_share],
                            'Total Change ($)': [total_change]
                        })
                        st.session_state.portfolio_df = pd.concat([df, new_row], ignore_index=True)
                    try:
                        log_transaction(datetime.now().strftime("%Y-%m-%d"), "Buy", ticker, shares, share_price,
                                        shares * share_price, notes)
                    except ValueError:
                        st.warning('Value Error: No Transactions Detected.')

                    st.session_state.portfolio_df.to_csv(CSV_FILE, index=False)
                    st.success(f"{ticker} saved to portfolio.")

        elif submitted_remove:
            if ticker == "":
                st.warning("Please enter a ticker symbol.")
            else:
                df = st.session_state.portfolio_df
                if ticker in df['Ticker'].values:
                    idx = df.index[df['Ticker'] == ticker][0]
                    current_shares = df.at[idx, 'Shares']
                    if shares > current_shares:
                        st.warning(f"You are trying to remove more shares ({shares}) than owned ({current_shares}).")
                    else:
                        yfinance_ticker = yf.Ticker(ticker)
                        share_price = yfinance_ticker.info.get('regularMarketPrice')
                        previous_close = yfinance_ticker.info.get('previousClose')

                        if share_price is None or previous_close is None:
                            st.warning(f"Could not fetch price data for {ticker}. Try again later.")
                        else:
                            new_share_count = current_shares - shares
                            price_change_per_share = share_price - previous_close

                            if new_share_count == 0:
                                st.session_state.portfolio_df = df.drop(idx).reset_index(drop=True)
                                st.success(f"All shares of {ticker} removed from portfolio.")
                            else:
                                df.at[idx, 'Shares'] = new_share_count
                                df.at[idx, 'Share Price ($)'] = share_price
                                df.at[idx, 'Total Value ($)'] = new_share_count * share_price
                                df.at[idx, 'Price Change Per Share ($)'] = price_change_per_share
                                df.at[idx, 'Total Change ($)'] = price_change_per_share * new_share_count
                                st.session_state.portfolio_df = df
                                st.success(f"{shares} shares of {ticker} removed.")
                            try:
                                log_transaction(datetime.now().strftime("%Y-%m-%d"), "Sell", ticker, shares,
                                                share_price, shares * share_price, notes)
                            except ValueError:
                                st.warning('Value Error: No Transactions Detected.')

                            st.session_state.portfolio_df.to_csv(CSV_FILE, index=False)
                else:
                    st.warning('Ticker not found in portfolio.')

    st.subheader("Current Portfolio")
    st.dataframe(st.session_state.portfolio_df, hide_index=True)

    # Portfolio summary
    df = st.session_state.portfolio_df
    total_stock_value = df['Total Value ($)'].sum() if not df.empty else 0.0
    total_change_value = df['Total Change ($)'].sum() if not df.empty else 0.0
    total_portfolio_value = total_stock_value + st.session_state.cash
    pct_change = (total_change_value / total_stock_value * 100) if total_stock_value > 0 else 0.0

    summary_df = pd.DataFrame({
        "Metric": [
            "Cash Assets",
            "Total Stock Value",
            "Total Portfolio Value",
            "Portfolio Change ($)",
            "Portfolio Change (%)"
        ],
        "Value": [
            f"${st.session_state.cash:,.2f}",
            f"${total_stock_value:,.2f}",
            f"${total_portfolio_value:,.2f}",
            f"${total_change_value:,.2f}",
            f"{pct_change:.2f}%"
        ]
    })

    st.subheader("Portfolio Summary")
    st.dataframe(summary_df, hide_index=True)



    # ---- Portfolio vs S&P 500 chart ----
    st.subheader("Portfolio Performance vs S&P 500")

    # Time range selector
    time_options = {
        "1 Month": 30,
        "3 Months": 90,
        "6 Months": 180,
        "1 Year": 365,
        "3 Years": 365 * 3,
        "5 Years": 365 * 5
    }
    time_choice = st.selectbox("Select Time Range", list(time_options.keys()), index=1)
    days = time_options[time_choice]

    # Build portfolio history
    if not df.empty:
        tickers = df['Ticker'].tolist()
        shares = df.set_index('Ticker')['Shares'].to_dict()
        start_date = datetime.today() - timedelta(days=days)

        # Fetch historical data
        portfolio_prices = yf.download(tickers, start=start_date, auto_adjust=True)['Close']
        if isinstance(portfolio_prices, pd.Series):  # Only one ticker
            portfolio_prices = portfolio_prices.to_frame()

        # Filter out tickers with no historical data (all NaN)
        valid_tickers = [t for t in tickers if t in portfolio_prices.columns and not portfolio_prices[t].isnull().all()]
        portfolio_prices = portfolio_prices[valid_tickers]
        shares = {t: shares[t] for t in valid_tickers}

        # Forward fill missing data to avoid NaNs and zeros disrupting the graph
        portfolio_prices = portfolio_prices.fillna(method='ffill')

        # Calculate portfolio value each day
        portfolio_value = portfolio_prices.multiply([shares[t] for t in portfolio_prices.columns], axis=1).sum(axis=1)
        portfolio_value = portfolio_value.dropna()
        portfolio_value = portfolio_value[portfolio_value > 0]

        # Fetch S&P 500 and fill missing data
        sp500 = yf.download("^GSPC", start=start_date, auto_adjust=True)['Close'].fillna(method='ffill')

        if portfolio_value.empty or pd.isna(portfolio_value.iloc[0]) or portfolio_value.iloc[0] == 0:
            st.warning("Portfolio price data incomplete or zero on first day; cannot display performance graph.")
        else:
            # Normalize to 100 for comparison
            portfolio_norm = portfolio_value / portfolio_value.iloc[0] * 100
            sp500_norm = sp500 / sp500.iloc[0] * 100

            comparison_df = pd.DataFrame({
                "Date": portfolio_norm.index,
                "Portfolio": pd.Series(portfolio_norm.values.ravel(), index=portfolio_norm.index),
                "S&P 500": pd.Series(sp500_norm.values.ravel(), index=sp500_norm.index)
            })

            fig = px.line(comparison_df, x="Date", y=["Portfolio", "S&P 500"], labels={"value": "Normalized Value"},
                          title=f"Portfolio vs S&P 500 ({time_choice})")
            st.plotly_chart(fig)
    else:
        st.info("Add some stocks to see performance comparison.")

    # ---- Sector pie chart ----
    if not df.empty:
        ticker_value_dict = {row['Ticker']: row['Total Value ($)'] for _, row in df.iterrows()}

        # Call Groq only if categories aren't already stored
        for ticker in ticker_value_dict:
            if ticker not in st.session_state.sector_data:
                prompt = (
                    f"Classify the company with ticker {ticker} into exactly one of these sectors: "
                    "Technology, Healthcare, Financials, Consumer Discretionary, Consumer Staples, "
                    "Energy, Industrials, Materials, Utilities, Real Estate, Communication Services. "
                    "Respond with only the sector name, nothing else."
                )
                try:
                    # noinspection PyTypeChecker
                    completion = client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[
                            {"role": "system",
                             "content": "You are a financial assistant that classifies companies into one of the provided sectors."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0
                    )
                    category = completion.choices[0].message.content.strip()
                    st.session_state.sector_data[ticker] = category
                except Exception as e:
                    st.warning(f"Groq error for {ticker}: {e}")


        # Group values by sector
        sector_totals = {}
        for ticker, value in ticker_value_dict.items():
            sector = st.session_state.sector_data.get(ticker, "Other")
            sector_totals[sector] = sector_totals.get(sector, 0) + value

        # Remove any categories with zero value
        filtered_sector_totals = {k: v for k, v in sector_totals.items() if v > 0}

        if not filtered_sector_totals:
            filtered_sector_totals = {"Other": 0}

        sector_df = pd.DataFrame(list(filtered_sector_totals.items()), columns=["Sector", "Value"])

        st.subheader("Portfolio Allocation by Sector")
        if not sector_df.empty:
            fig = px.pie(sector_df, values="Value", names="Sector", title="Sector Allocation")
            st.plotly_chart(fig)

    # Refresh button and last refresh time display
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Refresh Price Data"):
            for i, row in df.iterrows():
                ticker = row['Ticker']
                try:
                    yfinance_ticker = yf.Ticker(ticker)
                    share_price = yfinance_ticker.info.get('regularMarketPrice')
                    previous_close = yfinance_ticker.info.get('previousClose')

                    if share_price is not None and previous_close is not None:
                        share_price = float(share_price)
                        previous_close = float(previous_close)
                        shares = float(df.at[i, 'Shares'])

                        df.at[i, 'Share Price ($)'] = share_price
                        df.at[i, 'Total Value ($)'] = shares * share_price
                        df.at[i, 'Price Change Per Share ($)'] = share_price - previous_close
                        df.at[i, 'Total Change ($)'] = (share_price - previous_close) * shares
                except Exception as e:
                    st.warning(f"Error updating {ticker}: {e}")

            st.session_state.portfolio_df = df
            df.to_csv(CSV_FILE, index=False)
            st.session_state.last_refresh = datetime.now()
            save_last_refresh(st.session_state.last_refresh)
            st.success("Price data refreshed and saved.")
            st.rerun()

    with col2:
        if st.session_state.last_refresh:
            st.markdown(f"**Last refreshed:** {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.markdown("**Last refreshed:** Never")


