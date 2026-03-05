from __future__ import annotations

import hashlib
import json
import os
from typing import Dict, Any

from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod

# Algorand TestNet configuration (using public AlgoNode)
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""


class AlgorandClient:
    """
    Client for interacting with the Algorand blockchain to store data hashes/summaries.
    """

    def __init__(self, sender_mnemonic: str | None = None):
        """
        Initialize the Algorand client.
        :param sender_mnemonic: The 25-word mnemonic phrase for the wallet.
        """
        self.algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
        self.sender_mnemonic = sender_mnemonic or os.getenv("ALGORAND_MNEMONIC")
        
        if self.sender_mnemonic:
            try:
                self.private_key = mnemonic.to_private_key(self.sender_mnemonic)
                self.sender_address = account.address_from_private_key(self.private_key)
                print(f"BLOCKCHAIN: Initialized with address {self.sender_address}")
            except Exception as e:
                print(f"BLOCKCHAIN ERROR: Invalid mnemonic. Falling back to simulation mode. Details: {e}")
                self.private_key = None
                self.sender_address = "KE4JBJTAVEECFO7UCN45Y3UJHF7UXL4J4NE5ZKR4FU34JG7MHGCCQAHXEQ"
        else:
            print("BLOCKCHAIN: No ALGORAND_MNEMONIC found in environment.")
            self.private_key = None
            self.sender_address = "KE4JBJTAVEECFO7UCN45Y3UJHF7UXL4J4NE5ZKR4FU34JG7MHGCCQAHXEQ"

    def store_report_on_chain(self, report_text: str, report_metadata: Dict[str, Any]) -> str | None:
        """
        Stores the hash and summary of a fraud report on the Algorand blockchain.
        Returns the transaction ID if successful.
        """
        if not self.private_key:
            print("BLOCKCHAIN ERROR: No valid private key. Use a 25-word mnemonic.")
            return None

        # 1. Create a hash of the report for tamper-proofing
        report_hash = hashlib.sha256(report_text.encode()).hexdigest()
        
        # 2. Build the transaction note (limit 1KB)
        summary_str = f"Fraud Audit Report: {report_metadata.get('total_claims')} claims monitored. {report_metadata.get('suspicious_count')} suspicious patterns flagged. Tamper-proof Hash: {report_hash}"
        
        note_dict = {
            "message": summary_str,
            "app": "SurakshaNet",
            "report_hash": report_hash,
            "timestamp": report_metadata.get("timestamp"),
        }
        
        # Include any additional metadata (like quantum_seal_token)
        for key, value in report_metadata.items():
            if key not in note_dict:
                note_dict[key] = value
                
        note = json.dumps(note_dict).encode()

        try:
            # 3. Get suggested parameters
            params = self.algod_client.suggested_params()
            
            # 4. Create an unsigned transaction (0 ALGO payment to self)
            unsigned_txn = transaction.PaymentTxn(
                sender=self.sender_address,
                sp=params,
                receiver=self.sender_address,
                amt=0,
                note=note
            )

            # 5. Sign the transaction
            signed_txn = unsigned_txn.sign(self.private_key)

            # 6. Submit the transaction
            print(f"BLOCKCHAIN: Submitting transaction to {ALGOD_ADDRESS}...")
            txid = self.algod_client.send_transaction(signed_txn)
            print(f"BLOCKCHAIN: Transaction sent successfully! ID: {txid}")
            
            return txid

        except Exception as e:
            print(f"BLOCKCHAIN ERROR: {e}")
            return None

def wait_for_confirmation(client, txid):
    """
    Wait for a transaction to be confirmed on the blockchain.
    """
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print("Waiting for confirmation...")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print(f"Transaction confirmed in round {txinfo.get('confirmed-round')}.")
    return txinfo
