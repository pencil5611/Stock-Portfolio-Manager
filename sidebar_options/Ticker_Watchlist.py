import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, timezone
import os

WATCHLIST_FILE = 'watchlist.csv'


def load_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        df = pd.read_csv(WATCHLIST_FILE)
    else:
        df = pd.DataFrame(columns=[
            'Ticker', 'Price Now', 'Price 1M Ago', 'Price 3M Ago', 'Price 6M Ago',
            'Day % Change', '1M % Change', '3M % Change', '6M % Change'
        ])
    return df


def refresh_watchlist_data(watchlist_df):
    """Refresh all data for tickers in the watchlist"""
    if watchlist_df.empty:
        return watchlist_df

    updated_rows = []

    for _, row in watchlist_df.iterrows():
        ticker = row['Ticker']
        try:
            today = datetime.now(timezone.utc)
            one_month_ago = today - timedelta(days=30)
            three_months_ago = today - timedelta(days=90)
            six_months_ago = today - timedelta(days=182)
            ticker_yf = yf.Ticker(ticker)
            # Request extra days to account for weekends/holidays
            buffer_days = 30
            extended_start = six_months_ago - timedelta(days=buffer_days)
            hist = ticker_yf.history(start=extended_start.strftime('%Y-%m-%d'), end=today.strftime('%Y-%m-%d'))

            def get_price_on_or_before(date):
                if hist.empty:
                    return None

                date_str = date.strftime('%Y-%m-%d')

                # If exact date exists, return it
                if date_str in hist.index:
                    return hist.loc[date_str]['Close']

                # Convert to comparable format (remove timezone)
                hist_dates = pd.to_datetime([d.split()[0] for d in hist.index.astype(str)])
                target_date = pd.to_datetime(date_str)

                # If target date is before available data, use first available date
                if target_date < hist_dates.min():
                    first_date = hist_dates.min().strftime('%Y-%m-%d')
                    return hist.loc[first_date]['Close']

                # Otherwise find the closest date on or before target
                valid_dates = hist_dates[hist_dates <= target_date]
                if len(valid_dates) > 0:
                    closest_date = valid_dates.max().strftime('%Y-%m-%d')
                    return hist.loc[closest_date]['Close']

                return None


            price_1m = get_price_on_or_before(one_month_ago)
            price_3m = get_price_on_or_before(three_months_ago)
            price_6m = get_price_on_or_before(six_months_ago)
            share_price = ticker_yf.info.get('regularMarketPrice')
            last_close = ticker_yf.info.get('previousClose')

            price_time_list = [price_1m, price_3m, price_6m, share_price, last_close]

            if any(v is None for v in price_time_list):
                # Keep old data if refresh fails
                updated_rows.append(row.tolist())
                continue

            day_change = share_price - last_close
            month_change = share_price - price_1m
            threeM_change = share_price - price_3m
            sixM_change = share_price - price_6m

            day_pct = (day_change / last_close) * 100 if last_close else None
            month_pct = (month_change / price_1m) * 100 if price_1m else None
            threeM_pct = (threeM_change / price_3m) * 100 if price_3m else None
            sixM_pct = (sixM_change / price_6m) * 100 if price_6m else None

            updated_rows.append([
                ticker, share_price, price_1m, price_3m, price_6m,
                day_pct, month_pct, threeM_pct, sixM_pct
            ])

        except Exception as e:
            st.warning(f'Failed to refresh data for {ticker}: {e}')
            # Keep old data if refresh fails
            updated_rows.append(row.tolist())

    # Create new DataFrame with updated data
    updated_df = pd.DataFrame(updated_rows, columns=watchlist_df.columns)
    return updated_df


def show():
    st.title('Watchlist')

    if 'watchlist_df' not in st.session_state:
        st.session_state.watchlist_df = load_watchlist()

    # Add refresh button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button('🔄 Refresh All Data'):
            with st.spinner('Refreshing watchlist data...'):
                st.session_state.watchlist_df = refresh_watchlist_data(st.session_state.watchlist_df)
                st.session_state.watchlist_df.to_csv(WATCHLIST_FILE, index=False)
                st.success('Watchlist data refreshed!')
                st.rerun()

    with st.form('ticker_watchlist', clear_on_submit=True):
        ticker = st.text_input('Ticker Symbol').upper()
        submitted_ticker = st.form_submit_button('Add to Watchlist')
        submitted_remove = st.form_submit_button('Remove from Watchlist')

        if submitted_ticker:
            if ticker == '':
                st.warning('Please enter a ticker symbol')
            else:
                try:
                    today = datetime.now(timezone.utc)
                    one_month_ago = today - timedelta(days=30)
                    three_months_ago = today - timedelta(days=90)
                    six_months_ago = today - timedelta(days=182)
                    ticker_yf = yf.Ticker(ticker)
                    hist = ticker_yf.history(start=six_months_ago.strftime('%Y-%m-%d'), end=today.strftime('%Y-%m-%d'))

                    def get_price_on_or_before(date):
                        date_str = date.strftime('%Y-%m-%d')
                        while date_str not in hist.index and date > hist.index[0]:
                            date -= timedelta(days=1)
                            date_str = date.strftime('%Y-%m-%d')
                        return hist.loc[date_str]['Close'] if date_str in hist.index else None

                    price_1m = get_price_on_or_before(one_month_ago)
                    price_3m = get_price_on_or_before(three_months_ago)
                    price_6m = get_price_on_or_before(six_months_ago)
                    share_price = ticker_yf.info.get('regularMarketPrice')
                    last_close = ticker_yf.info.get('previousClose')




                    # Calculate changes safely
                    day_change = (share_price - last_close) if (
                                share_price is not None and last_close is not None) else None
                    month_change = (share_price - price_1m) if (
                                share_price is not None and price_1m is not None) else None
                    threeM_change = (share_price - price_3m) if (
                                share_price is not None and price_3m is not None) else None
                    sixM_change = (share_price - price_6m) if (
                                share_price is not None and price_6m is not None) else None

                    # Use original zero-division handling (which also handles None)
                    day_pct = (day_change / last_close) * 100 if last_close else None
                    month_pct = (month_change / price_1m) * 100 if price_1m else None
                    threeM_pct = (threeM_change / price_3m) * 100 if price_3m else None
                    sixM_pct = (sixM_change / price_6m) * 100 if price_6m else None

                    watchlist_df = st.session_state.watchlist_df

                    if ticker in watchlist_df['Ticker'].values:
                        watchlist_df.loc[watchlist_df['Ticker'] == ticker, :] = [
                            ticker, share_price, price_1m, price_3m, price_6m,
                            day_pct, month_pct, threeM_pct, sixM_pct
                        ]
                    else:
                        new_row = pd.DataFrame([[
                            ticker, share_price, price_1m, price_3m, price_6m,
                            day_pct, month_pct, threeM_pct, sixM_pct
                        ]], columns=watchlist_df.columns)
                        watchlist_df = pd.concat([watchlist_df, new_row], ignore_index=True)

                    watchlist_df.to_csv(WATCHLIST_FILE, index=False)
                    st.session_state.watchlist_df = watchlist_df

                    st.success(f'{ticker} added/updated in watchlist.')
                    st.rerun()
                except Exception as e:
                    st.error(f'Error retrieving data: {e}')

        if submitted_remove:
            if ticker == '':
                st.warning('Please enter a ticker symbol')
            else:
                try:
                    # Check if ticker exists in the DataFrame
                    if ticker in st.session_state.watchlist_df['Ticker'].values:
                        # Remove the row with matching ticker
                        st.session_state.watchlist_df = st.session_state.watchlist_df[
                            st.session_state.watchlist_df['Ticker'] != ticker
                            ]
                        # Save to CSV after removal
                        st.session_state.watchlist_df.to_csv(WATCHLIST_FILE, index=False)
                        st.success(f'Removed {ticker} from watchlist')
                        st.rerun()
                    else:
                        st.warning(f'{ticker} not found in watchlist')

                except Exception as e:
                    st.error(f'Error removing ticker: {e}')

    display_df = st.session_state.watchlist_df.copy()
    display_df = display_df.fillna('N/A')  # or 'Pending' or '--'
    st.dataframe(display_df, hide_index=True)










