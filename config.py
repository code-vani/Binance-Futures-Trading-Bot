"""
Configuration file for Trading Bot
Store your Binance API credentials here
"""

class Config:
    """Configuration settings for the trading bot"""
    
    # Binance API Credentials
    # IMPORTANT: Replace these with your actual Binance Testnet API credentials
    API_KEY = 'your api key '
    API_SECRET = 'your secret key '
    
    # Testnet Settings
    TESTNET = True
    TESTNET_BASE_URL = 'https://testnet.binancefuture.com'
    
    # Trading Parameters (Optional - can be customized)
    DEFAULT_LEVERAGE = 1
    DEFAULT_MARGIN_TYPE = 'ISOLATED'  # or 'CROSSED'
    
    # Risk Management (Optional)
    MAX_POSITION_SIZE = 1000  # Maximum position size in USDT
    MAX_ORDERS_PER_SYMBOL = 10
    
    # Logging Settings
    LOG_LEVEL = 'DEBUG'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_TO_FILE = True
    LOG_TO_CONSOLE = True
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return getattr(self, key, default)
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if cls.API_KEY == 'your api key ' or cls.API_SECRET == 'your secret key ':
            print("⚠️  WARNING: Please set your API credentials in config.py")
            return False
        return True

# Create a singleton instance
config = Config()
