"""
CLI Interface for Trading Bot
Provides an interactive command-line interface for trading operations
"""

import sys
from typing import Optional
from trading_bot import TradingBot
from config import Config
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
import json

console = Console()

class TradingCLI:
    """Command-line interface for the trading bot"""
    
    def __init__(self):
        """Initialize CLI"""
        self.bot: Optional[TradingBot] = None
        self.config = Config()
    
    def display_banner(self):
        """Display welcome banner"""
        banner = """
╔═══════════════════════════════════════════════════╗
║                                                   ║
║     🤖 BINANCE FUTURES TRADING BOT 🤖            ║
║                                                   ║
║     Testnet Environment - Safe Testing           ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
        """
        console.print(banner, style="bold cyan")
    
    def initialize_bot(self):
        """Initialize trading bot with credentials"""
        console.print("\n[bold yellow]Initializing Trading Bot...[/bold yellow]")
        
        api_key = self.config.get('API_KEY')
        api_secret = self.config.get('API_SECRET')
        
        if not api_key or not api_secret:
            console.print("[bold red]❌ API credentials not found![/bold red]")
            console.print("Please set API_KEY and API_SECRET in config.py")
            sys.exit(1)
        
        try:
            self.bot = TradingBot(api_key, api_secret, testnet=True)
            console.print("[bold green]✓ Bot initialized successfully![/bold green]")
            return True
        except Exception as e:
            console.print(f"[bold red]❌ Failed to initialize bot: {e}[/bold red]")
            return False
    
    def display_menu(self):
        """Display main menu"""
        menu = Table(show_header=False, box=box.ROUNDED, border_style="cyan")
        menu.add_column("Option", style="cyan", width=5)
        menu.add_column("Description", style="white")
        
        menu.add_row("1", "Place Market Order")
        menu.add_row("2", "Place Limit Order")
        menu.add_row("3", "Place Stop-Limit Order")
        menu.add_row("4", "Place TWAP Order (Advanced)")
        menu.add_row("5", "Place Grid Order (Advanced)")
        menu.add_row("6", "View Account Balance")
        menu.add_row("7", "View Open Orders")
        menu.add_row("8", "Cancel Order")
        menu.add_row("9", "Check Order Status")
        menu.add_row("10", "Get Current Price")
        menu.add_row("0", "Exit")
        
        console.print("\n")
        console.print(menu)
        console.print("\n")
    
    def get_input(self, prompt: str, input_type=str, required=True):
        """Get validated user input"""
        while True:
            try:
                value = console.input(f"[cyan]{prompt}:[/cyan] ").strip()
                
                if not value and required:
                    console.print("[red]This field is required![/red]")
                    continue
                
                if not value and not required:
                    return None
                
                if input_type == float:
                    return float(value)
                elif input_type == int:
                    return int(value)
                else:
                    return value
            except ValueError:
                console.print(f"[red]Invalid input! Please enter a valid {input_type.__name__}[/red]")
            except KeyboardInterrupt:
                console.print("\n[yellow]Operation cancelled[/yellow]")
                return None
    
    def place_market_order(self):
        """Handle market order placement"""
        console.print("\n[bold cyan]═══ Market Order ═══[/bold cyan]")
        
        symbol = self.get_input("Symbol (e.g., BTCUSDT)", str)
        if not symbol:
            return
        symbol = symbol.upper()
        
        if not self.bot.validate_symbol(symbol):
            console.print("[red]Invalid symbol![/red]")
            return
        
        current_price = self.bot.get_current_price(symbol)
        if current_price:
            console.print(f"[dim]Current price: {current_price}[/dim]")
        
        side = self.get_input("Side (BUY/SELL)", str)
        if not side:
            return
        side = side.upper()
        
        if side not in ['BUY', 'SELL']:
            console.print("[red]Invalid side! Must be BUY or SELL[/red]")
            return
        
        quantity = self.get_input("Quantity", float)
        if not quantity:
            return
        
        min_notional = self.bot.get_min_notional(symbol)
        if current_price and quantity * current_price < min_notional:
            console.print(f"[red]Order value too small! Minimum is {min_notional} USDT[/red]")
            return
        
        console.print(f"\n[yellow]Placing {side} market order for {quantity} {symbol}...[/yellow]")
        
        order = self.bot.place_market_order(symbol, side, quantity)
        
        if order:
            self.display_order_result(order)
        else:
            console.print("[red]❌ Order failed! Check logs for details.[/red]")
    
    def place_limit_order(self):
        """Handle limit order placement"""
        console.print("\n[bold cyan]═══ Limit Order ═══[/bold cyan]")
        
        symbol = self.get_input("Symbol (e.g., BTCUSDT)", str)
        if not symbol:
            return
        symbol = symbol.upper()
        
        if not self.bot.validate_symbol(symbol):
            console.print("[red]Invalid symbol![/red]")
            return
        
        current_price = self.bot.get_current_price(symbol)
        if current_price:
            console.print(f"[dim]Current price: {current_price}[/dim]")
        
        side = self.get_input("Side (BUY/SELL)", str)
        if not side:
            return
        side = side.upper()
        
        if side not in ['BUY', 'SELL']:
            console.print("[red]Invalid side![/red]")
            return
        
        quantity = self.get_input("Quantity", float)
        if not quantity:
            return
        
        price = self.get_input("Limit Price", float)
        if not price:
            return
        
        # Calculate valid price range (Binance typically allows ±5% for limit orders)
        if current_price:
            if side == 'BUY':
                max_buy_price = current_price * 1.05
                min_buy_price = current_price * 0.50  # Can buy at much lower prices
                
                if price > max_buy_price:
                    console.print(f"[yellow]⚠ Price too high! Maximum BUY price: {max_buy_price:.2f}[/yellow]")
                    console.print(f"[yellow]Adjusting price to {max_buy_price:.2f}...[/yellow]")
                    price = max_buy_price
                    
            else:  # SELL
                min_sell_price = current_price * 0.95
                max_sell_price = current_price * 2.0  # Can sell at much higher prices
                
                if price < min_sell_price:
                    console.print(f"[yellow]⚠ Price too low! Minimum SELL price: {min_sell_price:.2f}[/yellow]")
                    # Round UP to ensure we meet the minimum
                    adjusted_price = self.bot.round_to_tick_size(min_sell_price, symbol, round_up=True)
                    console.print(f"[yellow]Adjusting price to {adjusted_price:.2f}...[/yellow]")
                    price = adjusted_price
            
            deviation = abs(price - current_price) / current_price * 100
            if deviation > 10:
                console.print(f"[yellow]ℹ Price is {deviation:.1f}% away from market[/yellow]")
        
        console.print(f"\n[yellow]Placing {side} limit order for {quantity} {symbol} at {price}...[/yellow]")
        
        order = self.bot.place_limit_order(symbol, side, quantity, price)
        
        if order:
            self.display_order_result(order)
        else:
            console.print("[red]❌ Order failed! Check logs for details.[/red]")
    
    def place_stop_limit_order(self):
        """Handle stop-limit order placement"""
        console.print("\n[bold cyan]═══ Stop-Limit Order ═══[/bold cyan]")
        console.print("[dim]Stop-Limit: Order triggers at stop price, executes as limit order[/dim]\n")
        
        symbol = self.get_input("Symbol (e.g., BTCUSDT)", str)
        if not symbol:
            return
        symbol = symbol.upper()
        
        if not self.bot.validate_symbol(symbol):
            console.print("[red]Invalid symbol![/red]")
            return
        
        current_price = self.bot.get_current_price(symbol)
        if current_price:
            console.print(f"[dim]Current price: {current_price}[/dim]")
        
        side = self.get_input("Side (BUY/SELL)", str)
        if not side:
            return
        side = side.upper()
        
        if side not in ['BUY', 'SELL']:
            console.print("[red]Invalid side![/red]")
            return
        
        quantity = self.get_input("Quantity", float)
        if not quantity:
            return
        
        console.print("\n[dim]For SELL: Set stop price BELOW current price (stop-loss)[/dim]")
        console.print("[dim]For BUY: Set stop price ABOVE current price (buy breakout)[/dim]\n")
        
        stop_price = self.get_input("Stop Price (trigger price)", float)
        if not stop_price:
            return
        
        limit_price = self.get_input("Limit Price (execution price)", float)
        if not limit_price:
            return
        
        console.print(f"\n[yellow]Placing {side} stop-limit order...[/yellow]")
        
        order = self.bot.place_stop_limit_order(symbol, side, quantity, stop_price, limit_price)
        
        if order:
            self.display_order_result(order)
        else:
            console.print("[red]❌ Order failed! Check logs for details.[/red]")
    
    def place_twap_order(self):
        """Handle TWAP order placement"""
        console.print("\n[bold cyan]═══ TWAP Order (Time-Weighted Average Price) ═══[/bold cyan]")
        console.print("[dim]Splits your order into multiple smaller orders over time[/dim]\n")
        
        symbol = self.get_input("Symbol (e.g., BTCUSDT)", str)
        if not symbol:
            return
        symbol = symbol.upper()
        
        if not self.bot.validate_symbol(symbol):
            console.print("[red]Invalid symbol![/red]")
            return
        
        side = self.get_input("Side (BUY/SELL)", str)
        if not side:
            return
        side = side.upper()
        
        if side not in ['BUY', 'SELL']:
            console.print("[red]Invalid side![/red]")
            return
        
        total_quantity = self.get_input("Total Quantity", float)
        if not total_quantity:
            return
        
        duration = self.get_input("Duration (minutes)", int)
        if not duration:
            return
        
        num_orders = self.get_input("Number of orders to split into", int)
        if not num_orders:
            return
        
        # Show summary
        interval = duration / num_orders
        console.print(f"\n[dim]Summary:[/dim]")
        console.print(f"[dim]- {num_orders} orders of {total_quantity/num_orders:.3f} each[/dim]")
        console.print(f"[dim]- One order every {interval:.1f} minutes[/dim]")
        console.print(f"[dim]- Total time: {duration} minutes[/dim]\n")
        
        confirm = self.get_input("Continue? (yes/no)", str)
        if confirm.lower() not in ['yes', 'y']:
            console.print("[yellow]TWAP order cancelled[/yellow]")
            return
        
        console.print(f"\n[yellow]Placing TWAP order - {num_orders} orders over {duration} minutes...[/yellow]")
        console.print("[dim]This may take some time...[/dim]\n")
        
        orders = self.bot.place_twap_order(symbol, side, total_quantity, duration, num_orders)
        
        console.print(f"\n[green]✓ TWAP order completed: {len(orders)}/{num_orders} orders successful[/green]")
    
    def place_grid_order(self):
        """Handle Grid order placement"""
        console.print("\n[bold cyan]═══ Grid Order ═══[/bold cyan]")
        console.print("[dim]Places multiple limit orders at different price levels[/dim]\n")
        
        symbol = self.get_input("Symbol (e.g., BTCUSDT)", str)
        if not symbol:
            return
        symbol = symbol.upper()
        
        if not self.bot.validate_symbol(symbol):
            console.print("[red]Invalid symbol![/red]")
            return
        
        current_price = self.bot.get_current_price(symbol)
        if current_price:
            console.print(f"[dim]Current price: {current_price}[/dim]")
        
        side = self.get_input("Side (BUY/SELL)", str)
        if not side:
            return
        side = side.upper()
        
        if side not in ['BUY', 'SELL']:
            console.print("[red]Invalid side![/red]")
            return
        
        total_quantity = self.get_input("Total Quantity", float)
        if not total_quantity:
            return
        
        console.print(f"\n[dim]Recommended: Set prices within ±5% of current price[/dim]")
        
        lower_price = self.get_input("Lower Price", float)
        if not lower_price:
            return
        
        upper_price = self.get_input("Upper Price", float)
        if not upper_price:
            return
        
        if lower_price >= upper_price:
            console.print("[red]Lower price must be less than upper price![/red]")
            return
        
        num_grids = self.get_input("Number of grid levels", int)
        if not num_grids:
            return
        
        if num_grids < 2:
            console.print("[red]Need at least 2 grid levels![/red]")
            return
        
        # Adjust prices if needed for SELL orders
        if side == 'SELL' and current_price:
            min_sell_price = current_price * 0.95
            if lower_price < min_sell_price:
                # Round UP to meet minimum
                adjusted_lower = self.bot.round_to_tick_size(min_sell_price, symbol, round_up=True)
                console.print(f"[yellow]⚠ Adjusting lower price to {adjusted_lower:.2f} (5% rule)[/yellow]")
                lower_price = adjusted_lower
            if upper_price < min_sell_price:
                adjusted_upper = self.bot.round_to_tick_size(min_sell_price * 1.1, symbol, round_up=True)
                console.print(f"[yellow]⚠ Adjusting upper price to {adjusted_upper:.2f} (5% rule)[/yellow]")
                upper_price = adjusted_upper
        
        # Show summary
        price_step = (upper_price - lower_price) / (num_grids - 1)
        console.print(f"\n[dim]Summary:[/dim]")
        console.print(f"[dim]- {num_grids} orders of {total_quantity/num_grids:.3f} each[/dim]")
        console.print(f"[dim]- Price range: {lower_price:.2f} - {upper_price:.2f}[/dim]")
        console.print(f"[dim]- Price step: {price_step:.2f}[/dim]\n")
        
        confirm = self.get_input("Continue? (yes/no)", str)
        if confirm.lower() not in ['yes', 'y']:
            console.print("[yellow]Grid order cancelled[/yellow]")
            return
        
        console.print(f"\n[yellow]Placing Grid order with {num_grids} levels...[/yellow]")
        
        orders = self.bot.place_grid_order(symbol, side, total_quantity, lower_price, upper_price, num_grids)
        
        console.print(f"\n[green]✓ Grid order completed: {len(orders)}/{num_grids} orders successful[/green]")
    
    def view_balance(self):
        """Display account balance"""
        console.print("\n[bold cyan]═══ Account Balance ═══[/bold cyan]")
        
        balance = self.bot.get_account_balance()
        
        if balance:
            table = Table(show_header=True, box=box.ROUNDED, border_style="green")
            table.add_column("Asset", style="cyan")
            table.add_column("Balance", style="green", justify="right")
            table.add_column("Available", style="yellow", justify="right")
            
            for asset in balance:
                bal = float(asset['balance'])
                if bal > 0:
                    table.add_row(
                        asset['asset'],
                        f"{bal:.8f}",
                        asset['availableBalance']
                    )
            
            console.print(table)
        else:
            console.print("[red]Failed to fetch balance[/red]")
    
    def view_open_orders(self):
        """Display open orders"""
        console.print("\n[bold cyan]═══ Open Orders ═══[/bold cyan]")
        
        symbol = self.get_input("Symbol (leave empty for all)", str, required=False)
        
        orders = self.bot.get_open_orders(symbol.upper() if symbol else None)
        
        if orders is not None:
            if len(orders) == 0:
                console.print("[yellow]No open orders[/yellow]")
            else:
                table = Table(show_header=True, box=box.ROUNDED, border_style="cyan")
                table.add_column("Order ID", style="cyan")
                table.add_column("Symbol", style="white")
                table.add_column("Side", style="green")
                table.add_column("Type", style="yellow")
                table.add_column("Quantity", style="white", justify="right")
                table.add_column("Price", style="white", justify="right")
                
                for order in orders:
                    table.add_row(
                        str(order['orderId']),
                        order['symbol'],
                        order['side'],
                        order['type'],
                        order['origQty'],
                        order.get('price', 'MARKET')
                    )
                
                console.print(table)
        else:
            console.print("[red]Failed to fetch orders[/red]")
    
    def cancel_order(self):
        """Cancel an order"""
        console.print("\n[bold cyan]═══ Cancel Order ═══[/bold cyan]")
        console.print("[dim]Note: Cannot cancel already filled or expired orders[/dim]\n")
        
        symbol = self.get_input("Symbol", str)
        if not symbol:
            return
        symbol = symbol.upper()
        
        order_id = self.get_input("Order ID", int)
        if not order_id:
            return
        
        # Check order status first
        order = self.bot.get_order_status(symbol, order_id)
        if order:
            status = order.get('status', 'UNKNOWN')
            if status in ['FILLED', 'CANCELED', 'EXPIRED', 'REJECTED']:
                console.print(f"[yellow]⚠ Cannot cancel order - Status: {status}[/yellow]")
                return
        
        console.print(f"\n[yellow]Cancelling order {order_id}...[/yellow]")
        
        result = self.bot.cancel_order(symbol, order_id)
        
        if result:
            console.print("[green]✓ Order cancelled successfully![/green]")
        else:
            console.print("[red]❌ Failed to cancel order (may be filled or invalid)[/red]")
    
    def check_order_status(self):
        """Check order status"""
        console.print("\n[bold cyan]═══ Order Status ═══[/bold cyan]")
        
        symbol = self.get_input("Symbol", str)
        if not symbol:
            return
        symbol = symbol.upper()
        
        order_id = self.get_input("Order ID", int)
        if not order_id:
            return
        
        order = self.bot.get_order_status(symbol, order_id)
        
        if order:
            self.display_order_result(order)
        else:
            console.print("[red]Failed to fetch order status[/red]")
    
    def get_current_price(self):
        """Get current price for a symbol"""
        console.print("\n[bold cyan]═══ Current Price ═══[/bold cyan]")
        
        symbol = self.get_input("Symbol (e.g., BTCUSDT)", str)
        if not symbol:
            return
        symbol = symbol.upper()
        
        price = self.bot.get_current_price(symbol)
        
        if price:
            console.print(f"\n[green]✓ Current price for {symbol}: {price}[/green]")
        else:
            console.print("[red]Failed to fetch price[/red]")
    
    def display_order_result(self, order: dict):
        """Display order result in a formatted table"""
        table = Table(show_header=True, box=box.ROUNDED, border_style="green")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Order ID", str(order.get('orderId', 'N/A')))
        table.add_row("Symbol", order.get('symbol', 'N/A'))
        table.add_row("Side", order.get('side', 'N/A'))
        table.add_row("Type", order.get('type', 'N/A'))
        table.add_row("Status", order.get('status', 'N/A'))
        table.add_row("Quantity", str(order.get('origQty', 'N/A')))
        table.add_row("Price", str(order.get('price', '0.00')))
        table.add_row("Executed Qty", str(order.get('executedQty', '0.000')))
        
        if order.get('stopPrice'):
            table.add_row("Stop Price", str(order.get('stopPrice')))
        
        console.print("\n[bold green]✓ Order Details:[/bold green]")
        console.print(table)
    
    def run(self):
        """Main CLI loop"""
        self.display_banner()
        
        if not self.initialize_bot():
            return
        
        while True:
            try:
                self.display_menu()
                choice = self.get_input("Select an option", str)
                
                if choice == '1':
                    self.place_market_order()
                elif choice == '2':
                    self.place_limit_order()
                elif choice == '3':
                    self.place_stop_limit_order()
                elif choice == '4':
                    self.place_twap_order()
                elif choice == '5':
                    self.place_grid_order()
                elif choice == '6':
                    self.view_balance()
                elif choice == '7':
                    self.view_open_orders()
                elif choice == '8':
                    self.cancel_order()
                elif choice == '9':
                    self.check_order_status()
                elif choice == '10':
                    self.get_current_price()
                elif choice == '0':
                    console.print("\n[bold yellow]👋 Thank you for using the Trading Bot![/bold yellow]")
                    break
                else:
                    console.print("[red]Invalid option! Please try again.[/red]")
                
                console.input("\n[dim]Press Enter to continue...[/dim]")
                
            except KeyboardInterrupt:
                console.print("\n\n[bold yellow]👋 Goodbye![/bold yellow]")
                break
            except Exception as e:
                console.print(f"\n[red]Unexpected Error: {e}[/red]")
                console.input("\n[dim]Press Enter to continue...[/dim]")

if __name__ == "__main__":
    cli = TradingCLI()
    cli.run()