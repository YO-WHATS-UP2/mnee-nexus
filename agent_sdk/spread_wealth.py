import os
from dotenv import load_dotenv
from core import MneeAgent

load_dotenv()
ALICE_PK = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

def main():
    alice = MneeAgent("Alice", ALICE_PK)
    bob_address = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
    
    print(f"--- 💸 WEALTH TRANSFER ---")
    print(f"Alice has: {alice.w3.from_wei(alice.mnee.functions.balanceOf(alice.address).call(), 'ether')} MNEE")
    
    amount_to_send = 500_000 # Send half to Bob
    print(f"Sending {amount_to_send} MNEE to Bob...")
    
    # Send the transaction
    amount_wei = alice.w3.to_wei(amount_to_send, 'ether')
    alice._send_tx(alice.mnee.functions.transfer(bob_address, amount_wei))
    
    print("✅ Transfer Complete!")

if __name__ == "__main__":
    main()