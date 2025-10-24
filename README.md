# 🤖 Binance Futures Trading Bot

A comprehensive Python-based trading bot for Binance Futures Testnet with support for multiple order types, advanced trading strategies, and an interactive CLI interface.

## ✨ Features

### Core Functionality
- ✅ **Market Orders** - Instant execution at current market price
- ✅ **Limit Orders** - Execute at specific price levels
- ✅ **Stop-Limit Orders** - Conditional orders for risk management
- ✅ **TWAP Orders** - Time-Weighted Average Price strategy
- ✅ **Grid Trading** - Automated grid trading strategy
- ✅ **Order Management** - View, cancel, and track orders
- ✅ **Account Balance** - Real-time balance monitoring

### Technical Features
- 🔐 Secure API integration with Binance Futures Testnet
- 📊 Rich CLI interface with colored output
- 📝 Comprehensive logging system
- ⚠️ Robust error handling and validation
- 🎯 Automatic price rounding to tick size
- ⏱️ Server time synchronization
- 🛡️ Input validation and safety checks

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Binance Futures Testnet account ([Register here](https://testnet.binancefuture.com/))
- API Key and Secret from Binance Testnet

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/binance-trading-bot.git
cd binance-trading-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API credentials**
   
- Edit `config.py` and add your Binance Testnet API credentials:
```python
API_KEY = 'your_testnet_api_key_here'
API_SECRET = 'your_testnet_api_secret_here'
```

⚠️ **IMPORTANT**: Never commit your actual `config.py` file to GitHub!

### Running the Bot

**Windows:**
```bash
run_bot.bat
```

**Linux/Mac:**
```bash
python cli.py
```

## 📖 Usage Guide

### Main Menu Options

```
1. Place Market Order       - Execute immediately at market price
2. Place Limit Order        - Set specific price for execution
3. Place Stop-Limit Order   - Trigger order at stop price
4. Place TWAP Order         - Split order over time
5. Place Grid Order         - Multiple orders at price levels
6. View Account Balance     - Check available funds
7. View Open Orders         - List all pending orders
8. Cancel Order             - Cancel specific order
9. Check Order Status       - View order details
10. Get Current Price       - Check current market price
0. Exit                     - Close the application
```

### Example Workflows

#### Market Order
```
Symbol: BTCUSDT
Side: BUY
Quantity: 0.001
```

#### Limit Order
```
Symbol: ETHUSDT
Side: SELL
Quantity: 0.01
Limit Price: 4000.00
```

#### TWAP Order
```
Symbol: BTCUSDT
Side: BUY
Total Quantity: 0.003
Duration: 60 minutes
Number of Orders: 10
```

#### Grid Trading
```
Symbol: BTCUSDT
Side: BUY
Total Quantity: 0.005
Lower Price: 108000
Upper Price: 112000
Grid Levels: 5
```

## 🏗️ Project Structure

```
binance-trading-bot/
│
├── cli.py                  # Interactive CLI interface
├── trading_bot.py          # Core trading bot logic
├── config.py               # Configuration template
├── requirements.txt        # Python dependencies
├── run_bot.bat            # Windows startup script
├── .gitignore             # Git ignore rules
│
└── logs/                  # Trading logs (auto-generated)
    └── trading_bot_*.log
```

## 🔧 Configuration Options

Edit `config.py` to customize bot behavior:

```python
# Trading Parameters
DEFAULT_LEVERAGE = 1
DEFAULT_MARGIN_TYPE = 'ISOLATED'  # or 'CROSSED'

# Risk Management
MAX_POSITION_SIZE = 1000  # Maximum position in USDT
MAX_ORDERS_PER_SYMBOL = 10

# Logging
LOG_LEVEL = 'DEBUG'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_TO_FILE = True
LOG_TO_CONSOLE = True
```

## 📊 Logging

All trading activities are logged in the `logs/` directory with:
- API requests and responses
- Order execution details
- Errors and warnings
- Timestamps for all operations

## ⚠️ Safety Features

- ✅ Testnet-only operation (no real money at risk)
- ✅ Input validation for all parameters
- ✅ Automatic price rounding to exchange tick size
- ✅ Minimum notional value checks
- ✅ Order status verification before cancellation
- ✅ Server time synchronization to prevent timestamp errors

## 🐛 Troubleshooting

### Common Issues

**1. API Timestamp Error**
- Bot automatically syncs with server time
- If issues persist, check your system clock

**2. Price Tick Size Error**
- Bot automatically rounds prices to valid tick sizes
- Ensure prices are within ±5% of market price for limit orders

**3. Order Rejected**
- Check minimum notional value (usually 5 USDT)
- Verify symbol is valid on Binance Futures
- Ensure sufficient balance

**4. Unicode Display Issues (Windows)**
- Use `run_bot.bat` which sets UTF-8 encoding
- Or run: `chcp 65001` before starting Python

## 📝 API Rate Limits

Binance Testnet has the following limits:
- 1200 requests per minute
- 100 orders per 10 seconds per symbol
- Bot includes automatic delays to stay within limits

## 🔒 Security Best Practices

1. **Never share your API keys**
2. **Keep `config.py` private** (already in `.gitignore`)
3. **Use testnet only** for development and testing
4. **Enable IP whitelist** on Binance API settings
5. **Regularly rotate API keys**
6. **Set appropriate API permissions** (Futures Trading only)

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This bot is for **educational and testing purposes only**. It operates on Binance Testnet with virtual funds. 

**DO NOT use this bot with real money without:**
- Thorough testing
- Understanding of trading risks
- Proper risk management
- Professional financial advice

Trading cryptocurrencies involves substantial risk of loss. The authors are not responsible for any financial losses.

## 🙏 Acknowledgments

- [python-binance](https://github.com/sammchardy/python-binance) - Binance API wrapper
- [Rich](https://github.com/Textualize/rich) - Terminal formatting library
- Binance for providing testnet environment

https://github.com/user-attachments/assets/b7db7e2b-7e9b-47cf-8920-dffd1d93462f



## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**⭐ If you find this project helpful, please consider giving it a star!**


