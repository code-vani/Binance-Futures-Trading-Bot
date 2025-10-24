"""
Binance Futures Testnet Trading Bot
Author: Trading Bot Developer
Date: 2025-10-24
Description: A comprehensive trading bot supporting multiple order types for Binance Futures Testnet
"""

import logging
from datetime import datetime
from typing import Optional, Dict, List
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
import json
import time
import requests
from decimal import Decimal, ROUND_DOWN, ROUND_UP

class TradingBot:
    """
    A sophisticated trading bot for Binance Futures Testnet
    Supports: Market, Limit, Stop-Limit, TWAP, and Grid orders
    """
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """
        Initialize the trading bot
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            testnet: Use testnet environment (default: True)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        
        # Setup logging first
        self._setup_logging()
        
        # Initialize client with proper testnet configuration
        if testnet:
            self.client = Client(api_key, api_secret, testnet=True)
            # Set correct testnet URL
            self.client.API_URL = 'https://testnet.binancefuture.com'
            
            # CRITICAL FIX: Sync timestamp with server
            self._sync_time()
        else:
            self.client = Client(api_key, api_secret)
        
        self.logger.info("Trading Bot initialized successfully")
        self.logger.info(f"Testnet mode: {testnet}")
        
    def _sync_time(self):
        """Synchronize local time with Binance server time"""
        try:
            # Get server time directly from testnet
            response = requests.get('https://testnet.binancefuture.com/fapi/v1/time')
            server_time = response.json()['serverTime']
            local_time = int(time.time() * 1000)
            time_offset = server_time - local_time
            
            # Set timestamp offset
            self.client.timestamp_offset = time_offset
            print(f"✓ Time synced with server (offset: {time_offset}ms)")
            self.logger.info(f"Time synchronized - offset: {time_offset}ms")
        except Exception as e:
            print(f"⚠ Could not sync time, continuing with local time: {e}")
            self.logger.warning(f"Time sync failed: {e}")
            self.client.timestamp_offset = 0
        
    def _setup_logging(self):
        """Configure logging with both file and console handlers"""
        # Create logs directory if it doesn't exist
        import os
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Create logger
        self.logger = logging.getLogger('TradingBot')
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers = []
        
        # File handler with UTF-8 encoding
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        fh = logging.FileHandler(f'logs/trading_bot_{timestamp}.log', encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        
        # Console handler with UTF-8 encoding (Windows fix)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def _log_request(self, order_type: str, params: Dict):
        """Log API request details"""
        self.logger.info(f"API Request - Order Type: {order_type:<15}")
        self.logger.debug(f"Request Parameters: {json.dumps(params, indent=2)}")
    
    def _log_response(self, response: Dict):
        """Log API response details"""
        self.logger.info("API Response received")
        self.logger.debug(f"Response Data: {json.dumps(response, indent=2)}")
    
    def _log_error(self, error: Exception):
        """Log error details"""
        self.logger.error(f"Error occurred: {type(error).__name__}")
        self.logger.error(f"Error message: {str(error)}")
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """
        Get detailed symbol information including filters
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Symbol info dict or None
        """
        try:
            exchange_info = self.client.futures_exchange_info()
            for s in exchange_info['symbols']:
                if s['symbol'] == symbol.upper():
                    return s
            return None
        except Exception as e:
            self._log_error(e)
            return None
    
    def get_tick_size(self, symbol: str) -> float:
        """
        Get tick size (minimum price increment) for a symbol
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Tick size as float
        """
        try:
            symbol_info = self.get_symbol_info(symbol)
            if symbol_info:
                for f in symbol_info['filters']:
                    if f['filterType'] == 'PRICE_FILTER':
                        return float(f['tickSize'])
            return 0.1  # Default tick size
        except Exception as e:
            self._log_error(e)
            return 0.1
    
    def round_to_tick_size(self, price: float, symbol: str, round_up: bool = False) -> float:
        """
        Round price to valid tick size
        
        Args:
            price: Raw price
            symbol: Trading pair
            round_up: If True, round up instead of down
            
        Returns:
            Price rounded to tick size
        """
        tick_size = self.get_tick_size(symbol)
        
        # Convert to Decimal for precise rounding
        price_decimal = Decimal(str(price))
        tick_decimal = Decimal(str(tick_size))
        
        # Round to nearest tick
        if round_up:
            rounded = (price_decimal / tick_decimal).quantize(Decimal('1'), rounding=ROUND_UP) * tick_decimal
        else:
            rounded = (price_decimal / tick_decimal).quantize(Decimal('1'), rounding=ROUND_DOWN) * tick_decimal
        
        return float(rounded)
    
    def get_price_precision(self, symbol: str) -> tuple:
        """
        Get price and quantity precision for a symbol
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Tuple of (price_precision, quantity_precision)
        """
        try:
            symbol_info = self.get_symbol_info(symbol)
            if symbol_info:
                price_precision = symbol_info['pricePrecision']
                quantity_precision = symbol_info['quantityPrecision']
                return price_precision, quantity_precision
            return 2, 3  # Default values
        except Exception as e:
            self._log_error(e)
            return 2, 3
    
    def get_min_notional(self, symbol: str) -> float:
        """
        Get minimum notional value for a symbol
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Minimum notional value
        """
        try:
            symbol_info = self.get_symbol_info(symbol)
            if symbol_info:
                for f in symbol_info['filters']:
                    if f['filterType'] == 'MIN_NOTIONAL':
                        return float(f['notional'])
            return 5.0  # Default minimum
        except Exception as e:
            self._log_error(e)
            return 5.0
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate if trading symbol exists on Binance Futures
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            exchange_info = self.client.futures_exchange_info()
            symbols = [s['symbol'] for s in exchange_info['symbols']]
            is_valid = symbol.upper() in symbols
            
            if is_valid:
                self.logger.info(f"Symbol {symbol} validated successfully")
            else:
                self.logger.warning(f"Symbol {symbol} not found on Binance Futures")
            
            return is_valid
        except Exception as e:
            self._log_error(e)
            return False
    
    def get_account_balance(self) -> Optional[Dict]:
        """
        Get account balance information
        
        Returns:
            Dict with balance information or None if error
        """
        try:
            self.logger.info("Fetching account balance")
            balance = self.client.futures_account_balance()
            self._log_response(balance)
            return balance
        except Exception as e:
            self._log_error(e)
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current market price for a symbol
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Current price or None if error
        """
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol.upper())
            price = float(ticker['price'])
            self.logger.info(f"Current price for {symbol}: {price}")
            return price
        except Exception as e:
            self._log_error(e)
            return None
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> Optional[Dict]:
        """
        Place a market order
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            
        Returns:
            Order response or None if error
        """
        # Get precision and round quantity
        _, qty_precision = self.get_price_precision(symbol)
        quantity = round(quantity, qty_precision)
        
        params = {
            'symbol': symbol.upper(),
            'side': side.upper(),
            'type': 'MARKET',
            'quantity': quantity,
            'recvWindow': 60000
        }
        
        self._log_request('MARKET', params)
        
        try:
            order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side=side.upper(),
                type='MARKET',
                quantity=quantity,
                recvWindow=60000
            )
            
            self._log_response(order)
            self.logger.info(f"[OK] Market {side} order placed successfully")
            return order
            
        except BinanceAPIException as e:
            self._log_error(e)
            self.logger.error(f"Binance API Error: {e.message}")
            return None
        except Exception as e:
            self._log_error(e)
            return None
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, 
                         price: float, time_in_force: str = 'GTC') -> Optional[Dict]:
        """
        Place a limit order
        
        Args:
            symbol: Trading pair
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            price: Limit price
            time_in_force: Time in force (GTC, IOC, FOK)
            
        Returns:
            Order response or None if error
        """
        # Get precision
        price_precision, qty_precision = self.get_price_precision(symbol)
        
        # Round quantity
        quantity = round(quantity, qty_precision)
        
        # Round price to tick size - ROUND UP for adjusted prices to meet minimum
        price = self.round_to_tick_size(price, symbol, round_up=True)
        
        params = {
            'symbol': symbol.upper(),
            'side': side.upper(),
            'type': 'LIMIT',
            'quantity': quantity,
            'price': price,
            'timeInForce': time_in_force,
            'recvWindow': 60000
        }
        
        self._log_request('LIMIT', params)
        
        try:
            order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side=side.upper(),
                type='LIMIT',
                quantity=quantity,
                price=price,
                timeInForce=time_in_force,
                recvWindow=60000
            )
            
            self._log_response(order)
            self.logger.info(f"[OK] Limit {side} order placed successfully at {price}")
            return order
            
        except BinanceAPIException as e:
            self._log_error(e)
            self.logger.error(f"Binance API Error: {e.message}")
            return None
        except Exception as e:
            self._log_error(e)
            return None
    
    def place_stop_limit_order(self, symbol: str, side: str, quantity: float,
                              stop_price: float, limit_price: float) -> Optional[Dict]:
        """
        Place a stop-limit order (Stop-Loss or Take-Profit)
        
        Args:
            symbol: Trading pair
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            stop_price: Stop trigger price
            limit_price: Limit price after stop is triggered
            
        Returns:
            Order response or None if error
        """
        # Get precision
        price_precision, qty_precision = self.get_price_precision(symbol)
        
        # Round values
        quantity = round(quantity, qty_precision)
        stop_price = self.round_to_tick_size(stop_price, symbol)
        limit_price = self.round_to_tick_size(limit_price, symbol)
        
        params = {
            'symbol': symbol.upper(),
            'side': side.upper(),
            'type': 'STOP',
            'quantity': quantity,
            'stopPrice': stop_price,
            'price': limit_price,
            'recvWindow': 60000
        }
        
        self._log_request('STOP_LIMIT', params)
        
        try:
            order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side=side.upper(),
                type='STOP',
                quantity=quantity,
                price=limit_price,
                stopPrice=stop_price,
                timeInForce='GTC',
                recvWindow=60000
            )
            
            self._log_response(order)
            self.logger.info(f"[OK] Stop-Limit {side} order placed - Stop: {stop_price}, Limit: {limit_price}")
            return order
            
        except BinanceAPIException as e:
            self._log_error(e)
            self.logger.error(f"Binance API Error: {e.message}")
            return None
        except Exception as e:
            self._log_error(e)
            return None
    
    def place_twap_order(self, symbol: str, side: str, total_quantity: float,
                        duration_minutes: int, num_orders: int) -> List[Dict]:
        """
        Place a TWAP (Time-Weighted Average Price) order
        Splits order into multiple smaller orders over time
        
        Args:
            symbol: Trading pair
            side: 'BUY' or 'SELL'
            total_quantity: Total quantity to trade
            duration_minutes: Time period to spread orders
            num_orders: Number of orders to split into
            
        Returns:
            List of order responses
        """
        self.logger.info(f"Starting TWAP order - Symbol: {symbol}, Side: {side}")
        self.logger.info(f"Total Quantity: {total_quantity}, Duration: {duration_minutes}min, Orders: {num_orders}")
        
        orders = []
        _, qty_precision = self.get_price_precision(symbol)
        quantity_per_order = round(total_quantity / num_orders, qty_precision)
        interval_seconds = (duration_minutes * 60) / num_orders
        
        for i in range(num_orders):
            self.logger.info(f"Placing TWAP order {i+1}/{num_orders}")
            
            order = self.place_market_order(symbol, side, quantity_per_order)
            if order:
                orders.append(order)
                self.logger.info(f"[OK] TWAP order {i+1} executed")
            else:
                self.logger.error(f"[FAILED] TWAP order {i+1} failed")
            
            # Wait before next order (except for last one)
            if i < num_orders - 1:
                self.logger.info(f"Waiting {interval_seconds:.1f} seconds until next order")
                time.sleep(interval_seconds)
        
        self.logger.info(f"TWAP order completed - {len(orders)}/{num_orders} successful")
        return orders
    
    def place_grid_order(self, symbol: str, side: str, quantity: float,
                        lower_price: float, upper_price: float, 
                        num_grids: int) -> List[Dict]:
        """
        Place a Grid trading order
        Places multiple limit orders at different price levels
        
        Args:
            symbol: Trading pair
            side: 'BUY' or 'SELL'
            quantity: Total quantity to distribute
            lower_price: Lower price bound
            upper_price: Upper price bound
            num_grids: Number of grid levels
            
        Returns:
            List of order responses
        """
        self.logger.info(f"Starting Grid order - Symbol: {symbol}, Side: {side}")
        self.logger.info(f"Price Range: {lower_price} - {upper_price}, Grids: {num_grids}")
        
        orders = []
        price_precision, qty_precision = self.get_price_precision(symbol)
        quantity_per_grid = round(quantity / num_grids, qty_precision)
        price_step = (upper_price - lower_price) / (num_grids - 1)
        
        for i in range(num_grids):
            grid_price = lower_price + (i * price_step)
            # Round to tick size
            grid_price = self.round_to_tick_size(grid_price, symbol)
            
            self.logger.info(f"Placing grid order {i+1}/{num_grids} at price {grid_price}")
            
            order = self.place_limit_order(symbol, side, quantity_per_grid, grid_price)
            if order:
                orders.append(order)
                self.logger.info(f"[OK] Grid order {i+1} placed")
            else:
                self.logger.error(f"[FAILED] Grid order {i+1} failed")
            
            # Small delay to avoid rate limiting
            time.sleep(0.2)
        
        self.logger.info(f"Grid order completed - {len(orders)}/{num_grids} successful")
        return orders
    
    def cancel_order(self, symbol: str, order_id: int) -> Optional[Dict]:
        """
        Cancel an open order
        
        Args:
            symbol: Trading pair
            order_id: Order ID to cancel
            
        Returns:
            Cancellation response or None if error
        """
        try:
            self.logger.info(f"Cancelling order {order_id} for {symbol}")
            result = self.client.futures_cancel_order(
                symbol=symbol.upper(),
                orderId=order_id,
                recvWindow=60000
            )
            self._log_response(result)
            self.logger.info("[OK] Order cancelled successfully")
            return result
        except BinanceAPIException as e:
            self._log_error(e)
            self.logger.error(f"Binance API Error: {e.message}")
            return None
        except Exception as e:
            self._log_error(e)
            return None
    
    def get_open_orders(self, symbol: Optional[str] = None) -> Optional[List[Dict]]:
        """
        Get all open orders
        
        Args:
            symbol: Optional - filter by symbol
            
        Returns:
            List of open orders or None if error
        """
        try:
            self.logger.info(f"Fetching open orders{f' for {symbol}' if symbol else ''}")
            if symbol:
                orders = self.client.futures_get_open_orders(
                    symbol=symbol.upper(),
                    recvWindow=60000
                )
            else:
                orders = self.client.futures_get_open_orders(recvWindow=60000)
            
            self.logger.info(f"Found {len(orders)} open orders")
            return orders
        except Exception as e:
            self._log_error(e)
            return None
    
    def get_order_status(self, symbol: str, order_id: int) -> Optional[Dict]:
        """
        Check status of a specific order
        
        Args:
            symbol: Trading pair
            order_id: Order ID
            
        Returns:
            Order status or None if error
        """
        try:
            self.logger.info(f"Checking status for order {order_id}")
            order = self.client.futures_get_order(
                symbol=symbol.upper(),
                orderId=order_id,
                recvWindow=60000
            )
            self._log_response(order)
            return order
        except Exception as e:
            self._log_error(e)
            return None