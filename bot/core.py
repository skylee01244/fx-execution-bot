import time
import sys
from datetime import datetime
from .account import get_user_info, get_client_info, get_accounts, get_balance, get_positions, print_balance_summary, print_positions_summary
from .execution import get_fx_prices, place_limit_order, place_market_order, convert_to_market_order
from .utils import format_datetime

# Rich imports for professional terminal interface
try:
    from rich.console import Console
    from rich.live import Live
    from rich.table import Table
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class SaxoTradingBot:
    def __init__(self, access_token):
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        self.client_key = None
        self.account_key = None
        
        # UIC shortlist for display
        self.uic_shortlist = {
            16: "EUR/DKK",
            21: "EUR/USD", 
            31: "USD/JPY",
            22: "GBP/USD",
            17: "EUR/GBP",
        }

    def setup(self):
        """Fetch and set ClientKey and AccountKey"""
        user = get_user_info(self.headers)
        client = get_client_info(self.headers)
        accounts = get_accounts(self.headers)

        self.client_key = client['ClientKey']
        default_account_id = client['DefaultAccountId']

        for account in accounts['Data']:
            if account['AccountId'] == default_account_id:
                self.account_key = account['AccountKey']
                break

        print(f"ClientKey: {self.client_key}")
        print(f"AccountKey: {self.account_key}")

    def get_position_size(self, uic):
        """Get current position size for a given UIC. Returns (amount, symbol) or (0, None) if no position."""
        positions = get_positions(self.headers, self.client_key)
        
        for pos in positions.get("Data", []):
            base = pos.get("PositionBase", {})
            if str(base.get("Uic")) == str(uic):
                amount = int(base["Amount"])
                symbol = pos["DisplayAndFormat"]["Symbol"]
                return amount, symbol
        
        return 0, None

    def live_price_ticker(self, uics, update_interval=1):
        """Professional live price ticker using rich library"""
        if not RICH_AVAILABLE:
            print("❌ Rich library not available. Install with: pip install rich")
            return self._fallback_ticker(uics, update_interval)
        
        console = Console()
        prev_prices = {}
        start_time = time.time()
        
        def make_table() -> Table:
            table = Table(title="🚀 Live FX Market Data", box=box.ROUNDED)
            table.add_column("Symbol", style="cyan", no_wrap=True)
            table.add_column("Price", justify="right", style="bold")
            table.add_column("Bid", justify="right", style="dim")
            table.add_column("Ask", justify="right", style="dim")
            table.add_column("Change", justify="center")
            table.add_column("Time", style="dim", no_wrap=True)
            
            try:
                prices = get_fx_prices(self.headers, self.account_key, uics)
                current_time = datetime.now().strftime("%H:%M:%S")
                
                for i, uic in enumerate(uics):
                    try:
                        quote = prices['Data'][i]['Quote']
                        current_price = quote['Mid']
                        bid = quote.get('Bid', 0)
                        ask = quote.get('Ask', 0)
                        
                        symbol = self.uic_shortlist.get(uic, f"UIC {uic}")
                        
                        # Calculate change and direction
                        if uic in prev_prices:
                            prev_price = prev_prices[uic]
                            change = current_price - prev_price
                            change_pct = (change / prev_price) * 100 if prev_price != 0 else 0
                            
                            if change > 0:
                                change_text = Text(f"+{change:.5f} (+{change_pct:.2f}%)", style="green")
                                price_style = "green"
                            elif change < 0:
                                change_text = Text(f"{change:.5f} ({change_pct:.2f}%)", style="red")
                                price_style = "red"
                            else:
                                change_text = Text("0.00000 (0.00%)", style="yellow")
                                price_style = "yellow"
                        else:
                            change_text = Text("NEW", style="blue")
                            price_style = "blue"
                        
                        # Format price with proper styling
                        price_text = Text(f"{current_price:.5f}", style=price_style)
                        
                        table.add_row(
                            symbol,
                            price_text,
                            f"{bid:.5f}" if bid else "N/A",
                            f"{ask:.5f}" if ask else "N/A", 
                            change_text,
                            current_time
                        )
                        
                        prev_prices[uic] = current_price
                        
                    except (KeyError, IndexError, TypeError):
                        table.add_row(
                            f"UIC {uic}",
                            Text("ERROR", style="red"),
                            "N/A", "N/A",
                            Text("ERROR", style="red"),
                            current_time
                        )
                
            except Exception as e:
                table.add_row("API", "ERROR", "N/A", "N/A", Text("ERROR", style="red"), "ERROR")
            
            return table
        
        try:
            with Live(console=console, refresh_per_second=1/update_interval) as live:
                while True:
                    live.update(make_table())
                    time.sleep(update_interval)
                    
        except KeyboardInterrupt:
            console.print("\n[bold blue]⏹️  Stopped live ticker. Returning to main menu...[/bold blue]")
            time.sleep(1)

    def _fallback_ticker(self, uics, update_interval):
        """Fallback ticker without rich library"""
        print("\n🔄 Live Price Ticker (Press Ctrl+C to stop)")
        print("=" * 60)
        
        prev_prices = {}
        
        try:
            while True:
                prices = get_fx_prices(self.headers, self.account_key, uics)
                current_time = time.strftime("%H:%M:%S")
                
                sys.stdout.write('\033[2J\033[H')
                sys.stdout.flush()
                
                print(f"🔄 Live FX Prices - {current_time}")
                print("=" * 60)
                
                for i, uic in enumerate(uics):
                    try:
                        quote = prices['Data'][i]['Quote']
                        current_price = quote['Mid']
                        bid = quote.get('Bid', 'N/A')
                        ask = quote.get('Ask', 'N/A')
                        
                        if uic in prev_prices:
                            prev_price = prev_prices[uic]
                            if current_price > prev_price:
                                indicator = "🔼"
                                color = "\033[92m"
                            elif current_price < prev_price:
                                indicator = "🔽"
                                color = "\033[91m"
                            else:
                                indicator = "➡️"
                                color = "\033[93m"
                        else:
                            indicator = "🆕"
                            color = "\033[94m"
                        
                        symbol = self.uic_shortlist.get(uic, f"UIC {uic}")
                        price_str = f"{current_price:.5f}"
                        colored_price = f"{color}{price_str}\033[0m"
                        
                        print(f"{indicator} {symbol:12} | Price: {colored_price:>10} | Bid: {bid:>8} | Ask: {ask:>8}")
                        
                        prev_prices[uic] = current_price
                        
                    except (KeyError, IndexError, TypeError):
                        print(f"❌ UIC {uic} | Error fetching price data")
                
                print("\n" + "=" * 60)
                print("Press Ctrl+C to return to main menu")
                
                time.sleep(update_interval)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopped live ticker. Returning to main menu...")
            time.sleep(1)

    def manage_position(self, uic):
        positions = get_positions(self.headers, self.client_key)

        pos_data = None
        for pos in positions.get("Data", []):
            base = pos.get("PositionBase", {})
            if str(base.get("Uic")) == str(uic):
                pos_data = pos
                break

        if not pos_data:
            print("No open position found for this instrument.")
            return

        pnl = pos_data["PositionView"]["ProfitLossOnTradeInBaseCurrency"]
        amount = int(pos_data["PositionBase"]["Amount"])
        symbol = pos_data["DisplayAndFormat"]["Symbol"]
        open_price = pos_data["PositionBase"]["OpenPrice"]

        print(f"\nCurrent position for {symbol}:")
        print(f"Size: {amount:,}")
        print(f"Current Unrealized P&L: €{pnl:.2f}")
        print(f"Open Price: {open_price:.5f}")

        decision = input("Do you want to sell this position now? (y/n): ").strip().lower()
        if decision == 'y':
            print("Placing market sell order...")
            sell_resp = place_market_order(self.headers, self.account_key, uic=uic, amount=amount, buy_sell="Sell")
            print("Order response:", sell_resp)

            prices = get_fx_prices(self.headers, self.account_key, [uic])
            sell_price = prices['Data'][0]['Quote']['Mid']
            print(f"Sell Price (current market mid): {sell_price:.5f}")

            realized_pnl = (sell_price - open_price) * amount
            print(f"Realized P&L from this trade: €{realized_pnl:.2f}")
        else:
            print("Holding position.")

    def run(self):
        print("Getting user, client, and account info...")
        self.setup()

        def show_uic_shortlist():
            print("\nAvailable instruments (UIC: Symbol):")
            for uic, symbol in sorted(self.uic_shortlist.items()):
                print(f" {uic}: {symbol}")

        def prompt_uic(default_uic=None):
            while True:
                show_uic_shortlist()
                raw = input(f"Enter instrument UIC{f' (default {default_uic})' if default_uic else ''}: ").strip()
                if not raw and default_uic is not None:
                    return int(default_uic)
                if raw.isdigit():
                    return int(raw)
                print("Please enter a valid numeric UIC.")

        def prompt_multiple_uics():
            """Prompt for multiple UICs for live ticker"""
            show_uic_shortlist()
            print("\nEnter UICs separated by commas (e.g., 16,21,31) or press Enter for default (16,21):")
            raw = input("UICs: ").strip()
            
            if not raw:
                return [16, 21]  # Default to EUR/DKK and EUR/USD
            
            try:
                uics = [int(x.strip()) for x in raw.split(',')]
                return uics
            except ValueError:
                print("Invalid format. Using default UICs (16,21)")
                return [16, 21]

        def prompt_amount(default_amount=100000):
            while True:
                raw = input(f"Enter trade amount in units (default {default_amount}): ").strip().replace(",", "")
                if raw == "":
                    return int(default_amount)
                try:
                    val = int(float(raw))
                    if val > 0:
                        return val
                except ValueError:
                    pass
                print("Please enter a positive integer amount.")

        def show_menu():
            print("\n=== FX Trading Menu ===")
            print("1) Show account balance")
            print("2) Show current FX prices (single UIC)")
            print("3) Show open positions")
            print("4) Buy FX (market)")
            print("5) Sell FX (market)")
            print("6) Manage existing position by UIC (prompted)")
            print("7) 🔄 Live Price Ticker (real-time updates)")
            print("0) Exit")

        while True:
            show_menu()
            choice = input("Select an option: ").strip()

            if choice == '1':
                print("\nGetting account balance...")
                balance = get_balance(self.headers, self.client_key, self.account_key)
                print_balance_summary(balance)

            elif choice == '2':
                uic = prompt_uic(default_uic=16)
                print("\nFetching live FX price...")
                prices = get_fx_prices(self.headers, self.account_key, [uic])
                try:
                    quote = prices['Data'][0]['Quote']
                    mid = quote['Mid']
                    bid = quote.get('Bid')
                    ask = quote.get('Ask')
                    print(f"UIC {uic} | Mid: {mid} | Bid: {bid} | Ask: {ask}")
                except (KeyError, IndexError, TypeError):
                    print("Could not retrieve price data. Raw response:")
                    print(prices)

            elif choice == '3':
                print("\nFetching open positions...")
                positions = get_positions(self.headers, self.client_key)
                print_positions_summary(positions)

            elif choice == '4':
                uic = prompt_uic(default_uic=16)
                amount = prompt_amount()
                print("\nPlacing market BUY order...")
                resp = place_market_order(self.headers, self.account_key, uic=uic, amount=amount, buy_sell="Buy")
                print("Order response:", resp)

            elif choice == '5':
                uic = prompt_uic(default_uic=16)
                current_size, symbol = self.get_position_size(uic)
                
                if current_size == 0:
                    print(f"\n❌ No position found for UIC {uic}. You cannot sell what you don't own.")
                    print("💡 To open a short position, you need special permissions and margin requirements.")
                    continue
                
                print(f"\nCurrent position: {current_size:,} units of {symbol}")
                amount = prompt_amount()
                
                if amount > current_size:
                    print(f"\n❌ Cannot sell {amount:,} units - you only own {current_size:,} units.")
                    print("💡 You can only sell up to your current position size.")
                    continue
                
                print(f"\nPlacing market SELL order for {amount:,} units...")
                resp = place_market_order(self.headers, self.account_key, uic=uic, amount=amount, buy_sell="Sell")
                print("Order response:", resp)

            elif choice == '6':
                uic = prompt_uic(default_uic=16)
                self.manage_position(uic=uic)

            elif choice == '7':
                uics = prompt_multiple_uics()
                self.live_price_ticker(uics)

            elif choice == '0':
                print("\nExiting trading bot.")
                break

            else:
                print("Invalid option. Please choose from the menu.")
