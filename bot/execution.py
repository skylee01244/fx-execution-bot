import requests

BASE_URL = "https://gateway.saxobank.com/sim/openapi"


def get_fx_prices(headers, account_key, uics):
    uic_str = ",".join(str(uic) for uic in uics)
    url = (f"{BASE_URL}/trade/v1/infoprices/list?AccountKey={account_key}"
           f"&Uics={uic_str}&AssetType=FxSpot&Amount=100000&FieldGroups=DisplayAndFormat,Quote")
    return requests.get(url, headers=headers).json()

def place_limit_order(headers, account_key, uic, price, amount=100000):
    url = f"{BASE_URL}/trade/v2/orders"
    data = {
        "Uic": uic,
        "BuySell": "Buy",
        "AssetType": "FxSpot",
        "Amount": amount,
        "OrderPrice": price,
        "OrderType": "Limit",
        "OrderRelation": "StandAlone",
        "ManualOrder": True,
        "OrderDuration": {
            "DurationType": "GoodTillCancel"
        },
        "AccountKey": account_key
    }
    return requests.post(url, json=data, headers=headers).json()

def place_market_order(headers, account_key, uic, amount, buy_sell="Sell"):
    url = f"{BASE_URL}/trade/v2/orders"
    data = {
        "Uic": uic,
        "BuySell": buy_sell,
        "AssetType": "FxSpot",
        "Amount": amount,
        "OrderType": "Market",
        "OrderRelation": "StandAlone",
        "ManualOrder": True,
        "OrderDuration": {
            "DurationType": "DayOrder"
        },
        "AccountKey": account_key
    }
    return requests.post(url, json=data, headers=headers).json()

def convert_to_market_order(headers, account_key, order_id, uic):
    url = f"{BASE_URL}/trade/v2/orders"
    data = {
        "OrderType": "Market",
        "OrderDuration": {
            "DurationType": "DayOrder"
        },
        "AccountKey": account_key,
        "OrderId": order_id,
        "AssetType": "FxSpot"
    }
    return requests.patch(url, json=data, headers=headers).json()
