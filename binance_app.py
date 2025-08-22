import os
import requests
import hmac
import hashlib

# Get API keys from environment variables
API_KEY = os.environ.get("BINANCE_API_KEY")
API_SECRET = os.environ.get("BINANCE_API_SECRET")
BASE_URL = "https://api.binance.com"

def get_server_time():
    try:
        response = requests.get(f"{BASE_URL}/api/v3/time")
        response.raise_for_status()
        return response.json()["serverTime"]
    except Exception as e:
        print(f"Error getting server time: {e}")
        return None

def sign(params):
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def get_account_info():
    timestamp = get_server_time()
    if timestamp is None:
        return {"error": "Could not get server time"}
   
    params = {"timestamp": timestamp, "recvWindow": 10000}
    params["signature"] = sign(params)
    headers = {"X-MBX-APIKEY": API_KEY}
   
    try:
        response = requests.get(f"{BASE_URL}/api/v3/account", params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting account info: {e}")
        return {"error": str(e)}

def get_deposit_address(coin, network=None):
    timestamp = get_server_time()
    if timestamp is None:
        return {"error": "Could not get server time"}
   
    params = {"coin": coin, "timestamp": timestamp, "recvWindow": 10000}
    if network:
        params["network"] = network
    params["signature"] = sign(params)
    headers = {"X-MBX-APIKEY": API_KEY}
   
    try:
        response = requests.get(f"{BASE_URL}/sapi/v1/capital/deposit/address", params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting deposit address for {coin}: {e}")
        return {"error": str(e)}

def get_prices():
    try:
        response = requests.get(f"{BASE_URL}/api/v3/ticker/price")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting prices: {e}")
        return []

# Main execution
if __name__ == "__main__":
    if not API_KEY or not API_SECRET:
        print("Error: API keys not found in environment variables")
        exit(1)
   
    print("Starting Binance API App on Railway...")
    print("=" * 50)
   
    # Test server time
    server_time = get_server_time()
    if server_time:
        print(f"✓ Connected to Binance API")
        print(f"✓ Server time: {server_time}")
    else:
        print("✗ Failed to connect to Binance API")
        exit()
   
    # Get account info
    account = get_account_info()
    if "error" in account:
        print(f"✗ Error: {account['error']}")
    else:
        print("✓ Account info retrieved successfully")
        print(f"Account type: {account.get('accountType', 'N/A')}")
       
        # Show non-zero balances
        print("\n=== BALANCES ===")
        has_balance = False
        for b in account.get('balances', []):
            free = float(b['free'])
            locked = float(b['locked'])
            if free > 0 or locked > 0:
                print(f"{b['asset']}: Free={free}, Locked={locked}")
                has_balance = True
       
        if not has_balance:
            print("No balances found (account is empty)")
   
    # Show prices
    print("\n=== CURRENT PRICES ===")
    prices = get_prices()
    if prices:
        price_dict = {p['symbol']: p['price'] for p in prices}
        top_pairs = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
        for pair in top_pairs:
            if pair in price_dict:
                print(f"{pair}: ${price_dict[pair]}")
    else:
        print("Could not retrieve prices")
   
    print("\n" + "=" * 50)
    print("App is running successfully on Railway! 🚀")