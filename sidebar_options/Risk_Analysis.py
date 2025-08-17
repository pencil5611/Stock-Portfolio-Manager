import streamlit as st
from features.risk_analysis import *
from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv('API_KEY')

def show():
    try:
        st.title("📈 Stock Risk Analysis")
        ticker = st.text_input('Input Ticker you would like to analyze:')
        if ticker:
            stock, market = download_data(ticker)
            stock_returns = compute_daily_returns(stock)
            market_returns = compute_daily_returns(market)

            vol = calculate_volatility(stock_returns)
            beta = calculate_beta(stock_returns, market_returns)
            mdd = calculate_max_drawdown(stock)
            sharpe = calculate_sharpe_ratio(stock_returns)
            var_95 = calculate_var(stock_returns)

            st.markdown(f"""
            ### 📊 Risk Metrics for **{ticker.upper()}**
            - **Annualized Volatility:** {vol.item():.2%}
            - **Beta vs SPY:** {beta.item():.2f}
            - **Max Drawdown:** {mdd.item():.2%}
            - **Sharpe Ratio:** {sharpe.item():.2f}
            - **Value at Risk (95%):** {var_95.item():.2%}
            """)

            st.line_chart(stock)

            vol_val = vol.item()
            beta_val = beta.item()
            mdd_val = mdd.item()
            sharpe_val = sharpe.item()
            var_val = var_95.item()

            prompt = f"""
            Here are the risk metrics for {ticker.upper()}:
            - Annualized Volatility: {vol_val:.2%}
            - Beta vs SPY: {beta_val:.2f}
            - Max Drawdown: {mdd_val:.2%}
            - Sharpe Ratio: {sharpe_val:.2f}
            - 95% Value at Risk: {var_val:.2%}
    
            What is your analysis of this stock's risk profile?
            """


            if 'ai_client' not in st.session_state:
                st.session_state.ai_client = Groq(api_key=API_KEY)

            st.title('🤖 AI Analysis')
            client = st.session_state.ai_client
            system_prompt = {
                "role": "system",
                "content": "You are a professional quantitative finance expert specializing in stock risk analysis. "
            "Given the following stock risk metrics, provide a clear, concise, and insightful interpretation of each metric. "
            "Your explanation should:\n"
            "- Briefly define each metric\n"
            "- Interpret what the specific value means for the stock’s risk and return profile\n"
            "- Avoid contradictions or vague language\n"
            "- Summarize the overall risk profile based on the metrics\n"
            "- Suggest what kind of investor might be suited for this stock based on the risk\n"
            "- Use plain language suitable for an informed investor, avoiding jargon\n\n"
            }
            messages = [
                system_prompt,
                {"role": "user", "content": prompt}
            ]

            try:
                response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=messages,
                    temperature=0.1,
                    max_tokens=700
                )
                answer = response.choices[0].message.content.strip()
                st.markdown(f"**AI Response:** {answer}")
            except Exception as e:
                st.error(f"AI request failed: {e}")
    except IndexError:
        st.error('Error: Index Error')
