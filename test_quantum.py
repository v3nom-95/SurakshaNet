from fraud_detection_agent.blockchain.quantum_client import get_quantum_client

def test_quantum():
    client = get_quantum_client()
    print("Testing Quantum Entropy...")
    entropy = client.generate_quantum_entropy(256)
    print(f"Entropy: {entropy}")
    
    print("\nTesting Quantum Seal...")
    seal = client.create_quantum_seal("Test Payload")
    print(f"Seal: {seal}")

if __name__ == "__main__":
    test_quantum()
