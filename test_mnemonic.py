from algosdk import mnemonic
try:
    m = "ticket identify slice mirror science clean airport network cannon vote kidney coconut else toilet infant else equip only leader sniff tackle verb need yellow"
    print(f"Word count: {len(m.split())}")
    pk = mnemonic.to_private_key(m)
    print("Mnemonic is valid")
except Exception as e:
    print(f"Error: {e}")
