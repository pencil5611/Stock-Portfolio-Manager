# 📈 Stock Portfolio & Watchlist Manager

A comprehensive Streamlit web application for tracking your stock portfolio, monitoring watchlists, and analyzing performance with AI-powered insights.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.47+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### 📊 Portfolio Management
- **Real-time stock tracking** with live price updates
- **Position management** - buy/sell stocks with automatic calculations
- **Cash balance tracking** alongside stock holdings
- **Transaction history** logging for all buy/sell activities
- **Performance metrics** - daily, monthly, and portfolio-wide changes

### 📋 Advanced Watchlist
- **Multi-timeframe analysis** - 1M, 3M, and 6M price comparisons
- **Percentage change tracking** across all timeframes
- **One-click refresh** for all watchlist data
- **Smart data handling** for weekends and market holidays

### 📈 Analytics & Insights
- **Portfolio vs S&P 500** performance comparison charts
- **Sector allocation** pie charts with AI-powered categorization
- **Interactive time-range selection** (1M to 5Y)
- **Normalized performance tracking** for easy comparison

### 🤖 AI-Powered Features
- **Automatic sector categorization** using Groq's LLaMA models
- **Smart retry logic** for failed categorizations
- **11 major sector classifications** for comprehensive analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- A Groq API key (free at [console.groq.com](https://console.groq.com))
- A FinnHub API key (free at [Visit Finnhub Dashboard](https://finnhub.io/dashboard))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/pencil5611/Stock-Portfolio-Manager
cd Stock-Portfolio-Manager
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
Create a `.env` file in the project root:
```env
API_KEY=your_groq_api_key_here
FIN_API_KEY=your_fin_api_key_here
```

4. **Run the application**
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 🔑 Getting Your Groq API Key

1. Visit [console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Navigate to the [API Keys section](https://console.groq.com/keys)
4. Click "Create API Key"
5. Copy your key and add it to your `.env` file

*Note: Groq offers generous free tier limits for personal projects.*

## 📱 Usage Guide

### Portfolio Tab
1. **Add Cash**: Enter your available cash in the input field
2. **Add Stocks**: 
   - Enter ticker symbol (e.g., AAPL, TSLA)
   - Specify number of shares
   - Add optional notes
   - Click "Add Stock / Shares"
3. **Remove Positions**: Use the same form but click "Remove Stock / Shares"
4. **View Performance**: Check the portfolio summary and comparison charts

### Watchlist Tab
1. **Add to Watchlist**: Enter ticker and click "Add to Watchlist"
2. **Monitor Performance**: View price changes across multiple timeframes
3. **Refresh Data**: Use the "🔄 Refresh All Data" button for latest prices
4. **Remove Items**: Enter ticker and click "Remove from Watchlist"

## 📁 Project Structure

```
├── app.py                 # Main Streamlit application
├── features/              # Core functionality modules
│   ├── portfolio_manager.py       # Portfolio management
│   └── risk_analysis.py       # Watchlist functionality
├── sidebar_options/       # Navigation components
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 💾 Data Storage

All data is stored locally in CSV format:
- `portfolio.csv` - Your stock holdings and positions
- `watchlist.csv` - Monitored stocks with historical price data
- `transactions.csv` - Complete transaction history
- `cash.csv` - Current cash balance
- `last_refresh.txt` - Timestamp of last data refresh

*These files are automatically created and excluded from git commits.*

## 🎨 Customization

### Dark Theme (Optional)
Create `.streamlit/config.toml` for a custom dark theme:
```toml
[theme]
primaryColor = "#4CAF50"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
font = "sans serif"
```

### Sector Categories
The AI automatically categorizes stocks into:
- Technology
- Healthcare  
- Financials
- Consumer Discretionary
- Consumer Staples
- Energy
- Industrials
- Materials
- Utilities
- Real Estate
- Communication Services

## 🔧 Technical Details

### Dependencies
- **streamlit** - Web application framework
- **yfinance** - Real-time stock market data
- **pandas** - Data manipulation and analysis
- **plotly** - Interactive charts and visualizations
- **groq** - AI-powered sector categorization
- **python-dotenv** - Environment variable management

### Data Sources
- **Stock Prices**: Yahoo Finance via yfinance
- **Market Data**: Real-time and historical pricing
- **S&P 500**: ^GSPC index for performance comparison

### Smart Features
- **Weekend/Holiday Handling**: Automatically adjusts for non-trading days
- **Error Recovery**: Graceful handling of missing or delayed data
- **Session Persistence**: Maintains state across browser sessions
- **Automatic Refresh**: Built-in data refresh capabilities

## 🐛 Troubleshooting

### Common Issues

**"X time ago data is None"**
- This happens on weekends/holidays when 
- The refresh button will fix this on the next trading day (or sometimes within the hour)
- Data automatically resolves as calendar moves forward
- Note: This happens solely in the watchlist

**"Could not fetch price data"**
- Check your internet connection
- Verify ticker symbol is correct
- Try again during market hours
- Use the refresh button after a few minutes

**"Groq error for [ticker]"**
- Verify your API key is correctly set in `.env`
- Check you haven't exceeded free tier limits
- Failed categorizations will retry automatically

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit: `git commit -am 'Add new feature'`
5. Push: `git push origin feature-name`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Yahoo Finance](https://finance.yahoo.com) for providing free market data
- [Groq](https://groq.com) for fast AI inference
- [Streamlit](https://streamlit.io) for the amazing web app framework
- [FinnHub](https://finnhub.io) for news API
- The open-source community for the excellent Python libraries

---

**⭐ If you find this project helpful, please give it a star!**








