from dotenv import load_dotenv
load_dotenv()
from fraud_detection_agent.blockchain.algorand_client import AlgorandClient
import json

client = AlgorandClient()
print(f"Client Address: {client.sender_address}")
print(f"Private Key Set: {client.private_key is not None}")

txid = client.store_report_on_chain("Test Report", {"total_claims": 100, "suspicious_count": 5, "timestamp": "now"})
print(f"Transaction ID: {txid}")
