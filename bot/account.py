import requests
from .utils import format_datetime

BASE_URL = "https://gateway.saxobank.com/sim/openapi"


def get_user_info(headers):
    url = f"{BASE_URL}/port/v1/users/me"
    return requests.get(url, headers=headers).json()

def get_client_info(headers):
    url = f"{BASE_URL}/port/v1/clients/me"
    return requests.get(url, headers=headers).json()

def get_accounts(headers):
    url = f"{BASE_URL}/port/v1/accounts/me"
    return requests.get(url, headers=headers).json()

def get_balance(headers, client_key, account_key):
    url = f"{BASE_URL}/port/v1/balances?ClientKey={client_key}&AccountKey={account_key}"
    return requests.get(url, headers=headers).json()

def get_positions(headers, client_key):
    url = f"{BASE_URL}/port/v1/positions?ClientKey={client_key}&FieldGroups=DisplayAndFormat,PositionBase,PositionView"
    return requests.get(url, headers=headers).json()

def print_balance_summary(balance):
    print("\nAccount Balance Summary:")
    print("────────────────────────────")
    print(f"Currency: {balance.get('Currency', 'N/A')}")
    print(f"Cash Balance: €{balance.get('CashBalance', 0):,.2f}")
    print(f"Available for Trading: €{balance.get('CashAvailableForTrading', 0):,.2f}")
    print(f"Collateral Available: €{balance.get('CollateralAvailable', 0):,.2f}")
    print(f"Unrealized P&L: €{balance.get('UnrealizedMarginProfitLoss', 0):,.2f}")
    print(f"Total Account Value: €{balance.get('TotalValue', 0):,.2f}")
    print(f"Open Positions: {balance.get('OpenPositionsCount', 0)}")
    print(f"Margin Used: €{balance.get('MarginUsedByCurrentPositions', 0):,.2f} ({balance.get('MarginUtilizationPct', 0)}%)")

def print_positions_summary(positions):
    print("\nOpen Positions:")
    print("────────────────────────────────────────────")
    
    if not positions.get("Data"):
        print("No open positions found.")
        return

    for pos in positions["Data"]:
        fmt = pos["DisplayAndFormat"]
        base = pos["PositionBase"]
        view = pos["PositionView"]

        symbol = fmt["Symbol"]
        amount = int(base["Amount"])
        open_price = base["OpenPrice"]
        current_price = view["CurrentPrice"]
        pnl = view["ProfitLossOnTradeInBaseCurrency"]
        mv = view["MarketValueInBaseCurrency"]
        opened = format_datetime(base["ExecutionTimeOpen"])

        pos_id = pos.get("PositionId", "N/A")
        order_id = base.get("SourceOrderId", "N/A")

        print(f" {symbol} | Size: {amount:,} | Open: {open_price:.5f} → Current: {current_price:.5f}")
        print(f"   P&L: €{pnl:.2f} | Market Value: €{mv:.2f} | Opened: {opened}")
        print(f"   Position ID: {pos_id} | Order ID: {order_id}\n")
