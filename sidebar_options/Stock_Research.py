import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
import requests
import os
from dotenv import load_dotenv
from groq import Groq
import re

load_dotenv()
API_KEY = os.getenv("FIN_API_KEY")
groq_key = os.getenv("API_KEY")

groq_client = Groq(api_key=groq_key)


def show():
    st.title('Stock Research')

   
    with st.form('ticker_form', clear_on_submit=False):
        ticker = st.text_input('Ticker Symbol').upper()
        submitted = st.form_submit_button('Fetch Data')

    
    if 'metrics_df' not in st.session_state:
        st.session_state.metrics_df = pd.DataFrame()
    if 'ticker_prices_df' not in st.session_state:
        st.session_state.ticker_prices_df = pd.DataFrame()

    
    if submitted and ticker:
        
        st.session_state['ticker'] = ticker

        yf_ticker = yf.Ticker(ticker)
        hist = yf_ticker.history(period="7d")
        if hist.empty:
            st.error(f'Could not fetch price data for "{ticker}"')
            st.stop()
        else:
            st.session_state.ticker_prices_df = hist[['Close']].copy()

            
            info = yf_ticker.info
            metrics = {
                'Current Price': info.get('regularMarketPrice'),
                'Previous Close': info.get('previousClose'),
                'Open': info.get('open'),
                'Days Low': info.get('dayLow'),
                'Days High': info.get('dayHigh'),
                'Fifty Two Week Low': info.get('fiftyTwoWeekLow'),
                'Fifty Two Week High': info.get('fiftyTwoWeekHigh'),
                'Volume': info.get('volume'),
                'Average Volume': info.get('averageVolume'),
                'Market Cap': info.get('marketCap'),
                'Beta': info.get('beta'),
                'PE Ratio': info.get('trailingPE'),
                'EPS': info.get('trailingEps'),
                'Target Price': info.get('targetMeanPrice'),
            }

            def format_value(val):
                if val is None:
                    return 'N/A'
                if isinstance(val, (int, float)):
                    return f"{val:,.2f}"
                if isinstance(val, datetime):
                    return val.strftime('%b %d, %Y')
                return str(val)

            metrics_formatted = {k: format_value(v) for k, v in metrics.items()}
            st.session_state.metrics_df = pd.DataFrame([metrics_formatted])

    
    if 'ticker' in st.session_state:
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
        start_date = datetime.today() - timedelta(days=days)

        
        ticker_prices = yf.download(st.session_state['ticker'], start=start_date, auto_adjust=True)['Close'].fillna(
            method='ffill')

        
        st.session_state.ticker_prices_df = pd.DataFrame(
            {'Date': ticker_prices.index.ravel(), 'Close': ticker_prices.values.ravel()})

        
        if not st.session_state.ticker_prices_df.empty:
            df = st.session_state.ticker_prices_df.set_index('Date')
            st.line_chart(df['Close'])

        
        if not st.session_state.metrics_df.empty:
            st.subheader('Important Metrics')
            metrics_dict = st.session_state.metrics_df.iloc[0].to_dict()

            formatted_lines = []
            for key, value in metrics_dict.items():
                
                formatted_lines.append(f"**{key}** {'.' * 20} <span style='color: #00cc44;'>{value}</span>")

            
            st.markdown('<br>'.join(formatted_lines), unsafe_allow_html=True)

        
        if 'show_news' not in st.session_state:
            st.session_state.show_news = False
        if 'show_ai' not in st.session_state:
            st.session_state.show_ai = False

        stored_ticker = st.session_state['ticker']
        col1, col2 = st.columns(2)

        with col1:
            if st.button(f'{stored_ticker} News'):
                st.session_state.show_news = True
                st.session_state.show_ai = False

        with col2:
            if st.button(f'{stored_ticker} AI Overview'):
                st.session_state.show_ai = True
                st.session_state.show_news = False

        if st.session_state.show_news:
            try:
                if stored_ticker == '':
                    st.warning('Please enter a ticker symbol')
                else:
                    two_months_ago = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
                    today = datetime.now().strftime('%Y-%m-%d')
                    url = f"https://finnhub.io/api/v1/company-news?symbol={stored_ticker}&from={two_months_ago}&to={today}&token={API_KEY}"
                    response = requests.get(url)
                    news_data = response.json()
                    if response.status_code == 200:
                        with st.container():
                            for article in news_data:
                                st.markdown(f"### [{article['headline']}]({article['url']})")
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    readable_date = datetime.fromtimestamp(article['datetime']).strftime(
                                        '%B %d, %Y at %I:%M %p')
                                    st.caption(f"📅 {readable_date}")
                                with col2:
                                    st.caption(f"📰 {article['source']}")
                                with col3:
                                    st.caption(f"📊 Sentiment: {article.get('sentiment', 'N/A')}")

                                # Summary/content
                                st.markdown(article['summary'])
                                st.divider()
            except Exception as e:
                st.error(e)

        if st.session_state.show_ai:
            try:
                if stored_ticker == '':
                    st.warning('Please enter a ticker symbol')
                else:
                    yf_ticker = yf.Ticker(stored_ticker)
                    info = yf_ticker.info
                    metrics = {
                        'Current Price': info.get('regularMarketPrice'),
                        'Previous Close': info.get('previousClose'),
                        'Open': info.get('open'),
                        'Days Low': info.get('dayLow'),
                        'Days High': info.get('dayHigh'),
                        'Fifty Two Week Low': info.get('fiftyTwoWeekLow'),
                        'Fifty Two Week High': info.get('fiftyTwoWeekHigh'),
                        'Volume': info.get('volume'),
                        'Average Volume': info.get('averageVolume'),
                        'Market Cap': info.get('marketCap'),
                        'Beta': info.get('beta'),
                        'PE Ratio': info.get('trailingPE'),
                        'EPS': info.get('trailingEps'),
                        'Target Price': info.get('targetMeanPrice'),
                    }

                    def format_value(val):
                        if val is None:
                            return 'N/A'
                        if isinstance(val, (int, float)):
                            return f"{val:,.2f}"
                        if isinstance(val, datetime):
                            return val.strftime('%b %d, %Y')
                        return str(val)

                    metrics_formatted = {k: format_value(v) for k, v in metrics.items()}
                    cleaned_metrics = {k: re.sub(r'\s+', ' ', str(v)) for k, v in metrics_formatted.items()}

                    price_data = f"Current: ${cleaned_metrics['Current Price']}, Previous Close: ${cleaned_metrics['Previous Close']}, Open: ${cleaned_metrics['Open']}"

                    range_data = f"Day Range: ${cleaned_metrics['Days Low']} - ${cleaned_metrics['Days High']}, 52-Week Range: ${cleaned_metrics['Fifty Two Week Low']} - ${cleaned_metrics['Fifty Two Week High']}"

                    volume_data = f"Volume: {cleaned_metrics['Volume']}, Average Volume: {cleaned_metrics['Average Volume']}"

                    valuation_data = f"Market Cap: ${cleaned_metrics['Market Cap']}, PE Ratio: {cleaned_metrics['PE Ratio']}, EPS: ${cleaned_metrics['EPS']}"

                    risk_data = f"Beta: {cleaned_metrics['Beta']}, Target Price: ${cleaned_metrics['Target Price']}"

                    prompt = f"""
                    Analyze {stored_ticker} using these grouped financial metrics:

                    PRICING: {price_data}
                    TRADING RANGES: {range_data}
                    VOLUME: {volume_data}
                    VALUATION: {valuation_data}
                    RISK & TARGETS: {risk_data}

                    Provide a professional investment analysis covering company overview, financial health, valuation, and outlook.
                    """

                    try:
                        # noinspection PyTypeChecker
                        response = groq_client.chat.completions.create(
                            model="llama3-8b-8192",
                            messages=[
                                {"role": "system",
                                 "content": """You are a financial analyst. When given stock data, provide a clear, detailed, and professional summary of the company's financial condition and investment analysis.

                    Instructions for your analysis:
                    1. **Company Overview** — Briefly describe what the company does
                    2. **Financial Health** — Discuss profitability, liquidity, leverage, and efficiency 
                    3. **Growth & Trends** — Identify trends and growth patterns
                    4. **Valuation** — Analyze if the stock might be overvalued or undervalued
                    5. **Risks & Concerns** — Highlight any red flags or concerning ratios
                    6. **Investment Outlook** — Provide a reasoned investment outlook

                    CRITICAL: Always use proper spacing between words. Never concatenate words together. Each word should be separated by exactly one space.

                    Keep your tone objective and data driven.
                    CRITICAL FORMATTING: Write each word separately. For example, write "the company is profitable" NOT "thecompanyisprofitable". Always put spaces between words."""},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.1
                        )
                        analysis = response.choices[0].message.content.strip()

                        st.subheader('**🤖 AI Analysis**')
                        st.markdown(analysis)
                    except Exception as e:
                        st.error(f"AI request failed: {e}")
            except Exception as e:
                st.error(f"AI request failed: {e}")











