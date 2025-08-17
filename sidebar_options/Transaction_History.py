import streamlit as st
import pandas as pd
import os

def show():
    TRANSACTIONS_FILE = "transactions.csv"

    # Load transaction data
    if os.path.exists(TRANSACTIONS_FILE):
        df = pd.read_csv(TRANSACTIONS_FILE, parse_dates=["Date"])
    else:
        df = pd.DataFrame(columns=["Date", "Type", "Ticker", "Shares", "Price Per Share", "Total Value", "Notes"])

    st.title("📜 Transaction History")

    try:
        if not df.empty:
            min_date = df["Date"].min()
            max_date = df["Date"].max()
            start_date, end_date = st.date_input("Filter by date range", [min_date, max_date])


            tickers = ["All"] + sorted(df["Ticker"].dropna().unique().tolist())
            selected_ticker = st.selectbox("Filter by ticker", tickers)

            txn_types = ["All"] + sorted(df["Type"].dropna().unique().tolist())
            selected_type = st.selectbox("Filter by transaction type", txn_types)

            filtered_df = df[
                (df["Date"] >= pd.to_datetime(start_date)) &
                (df["Date"] <= pd.to_datetime(end_date))
            ]

            if selected_ticker != "All":
                filtered_df = filtered_df[filtered_df["Ticker"] == selected_ticker]

            if selected_type != "All":
                filtered_df = filtered_df[filtered_df["Type"] == selected_type]

            if not filtered_df.empty:
                selected_rows = st.multiselect(
                    "Select transactions to delete",
                    options=filtered_df.index,
                    format_func=lambda x: f"{filtered_df.loc[x, 'Date'].date()} | {filtered_df.loc[x, 'Ticker']} | {filtered_df.loc[x, 'Type']}"
                )
                if st.button("🗑 Delete Selected Transactions", type="primary"):
                    df = df.drop(selected_rows)
                    df.to_csv(TRANSACTIONS_FILE, index=False)
                    st.success("Selected transactions deleted.")
                    st.rerun()

            st.dataframe(filtered_df.sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True)
        else:
            st.warning("No transactions detected.")
    except ValueError:
        st.warning('Value Error: No Transactions Detected.')





