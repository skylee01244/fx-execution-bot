import time
from .account import get_user_info, get_client_info, get_accounts, get_balance, get_positions, print_balance_summary, print_positions_summary
from .execution import get_fx_prices, place_limit_order, place_market_order, convert_to_market_order
from .utils import format_datetime


class SaxoTradingBot:
    def __init__(self, access_token):
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        self.client_key = None
        self.account_key = None

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

        while True:
            print("\nGetting account balance...")
            balance = get_balance(self.headers, self.client_key, self.account_key)
            print_balance_summary(balance)

            print("\nFetching live FX prices...")
            uics = [16]  # EURDKK
            prices = get_fx_prices(self.headers, self.account_key, uics)
            eur_dkk_price = prices['Data'][0]['Quote']['Mid']
            print(f"EUR/DKK price: {eur_dkk_price}")

            print("\nFetching updated positions...")
            positions = get_positions(self.headers, self.client_key)
            print_positions_summary(positions)

            # Ask to sell position if any
            self.manage_position(uic=16)

            cont = input("\nDo you want to continue trading? (y/n): ").strip().lower()
            if cont != 'y':
                print("\nExiting trading bot.")
                break

            print("\nWaiting 5 seconds before next cycle...\n")
            time.sleep(5)
