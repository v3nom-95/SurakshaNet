import requests
try:
    resp = requests.get("http://localhost:8001/generate-report?state=All&district=All", timeout=30)
    data = resp.json()
    print("KEYS:", data.keys())
    print("TXID:", data.get("blockchain_tx_id"))
    print("WALLET:", data.get("wallet_address"))
except Exception as e:
    print(f"ERROR: {e}")
