from algosdk import mnemonic, account
import os
from dotenv import load_dotenv

load_dotenv()
m = os.getenv("ALGORAND_MNEMONIC")
print(f"Mnemonic from .env: {m}")
try:
    pk = mnemonic.to_private_key(m)
    addr = account.address_from_private_key(pk)
    print(f"SUCCESS: Address is {addr}")
except Exception as e:
    print(f"FAILURE: {e}")
