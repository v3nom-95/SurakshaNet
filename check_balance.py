from algosdk.v2client import algod
import os
from dotenv import load_dotenv
from algosdk import mnemonic, account

load_dotenv()
m = os.getenv("ALGORAND_MNEMONIC")
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""

client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
try:
    pk = mnemonic.to_private_key(m)
    addr = account.address_from_private_key(pk)
    account_info = client.account_info(addr)
    balance = account_info.get('amount')
    print(f"Address: {addr}")
    print(f"Balance: {balance} microAlgos")
    if balance < 1000:
        print("WARNING: Insufficient balance for transaction fee (0.001 ALGO = 1000 microAlgos)")
except Exception as e:
    print(f"ERROR: {e}")
