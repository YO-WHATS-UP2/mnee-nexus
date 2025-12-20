import os
from dotenv import load_dotenv
from core import MneeAgent

# Anvil Private Keys
ALICE_PK = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
BOB_PK = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"

def main():
    print("--- DIAGNOSTIC HIRE ---")
    alice = MneeAgent("Alice", ALICE_PK)
    bob = MneeAgent("Bob", BOB_PK)

    # 1. Register (if needed)
    try:
        alice.register_service("PYTHON_DEV", 100)
    except:
        pass # Ignore if already registered

    print(f"\n[Bob] Attempting to hire Alice...")
    
    # 2. Approve
    bob.approve_token(bob.escrow.address, 100)
    
    # 3. Create Task & INSPECT RECEIPT
    payment_wei = bob.w3.to_wei(100, 'ether')
    
    # Manually build tx to inspect result
    func = bob.escrow.functions.createTask(alice.address, payment_wei)
    receipt = bob._send_tx(func)

    print("\n--- TRANSACTION RESULT ---")
    print(f"Tx Hash: {receipt.transactionHash.hex()}")
    
    if receipt.status == 1:
        print("✅ Status: SUCCESS (1)")
        print(f"📄 Logs Generated: {len(receipt.logs)}")
        if len(receipt.logs) > 0:
            print("   (Events exist! The listener is just missing them.)")
        else:
            print("   ⚠️ WARNING: Transaction succeeded but NO EVENTS were emitted.")
    else:
        print("❌ Status: FAILED (0) - Transaction Reverted!")
        print("   (Check: Does Bob have enough MNEE? Did he approve enough?)")

if __name__ == "__main__":
    main()