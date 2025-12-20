import time
import os
from dotenv import load_dotenv
from core import MneeAgent

# Load Env
load_dotenv()
ALICE_PK = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

def main():
    alice = MneeAgent("Alice", ALICE_PK)
    
    print(f"--- 🎧 Alice is Listening for Jobs ---")
    print(f"Address: {alice.address}")
    print(f"Escrow:  {alice.escrow.address}")

    # Start listening from the current block
    current_block = alice.w3.eth.block_number
    print(f"Started at Block: {current_block}")
    print("Waiting for events (Press Ctrl+C to stop)...")

    while True:
        try:
            latest_block = alice.w3.eth.block_number
            
            if latest_block > current_block:
                # Scan new blocks
                print(f"Scanning blocks {current_block + 1} -> {latest_block}...")
                
                # Correct Snake Case arguments for modern web3.py
                events = alice.escrow.events.TaskCreated.get_logs(
                    from_block=current_block + 1,
                    to_block=latest_block
                )
                
                for event in events:
                    args = event['args']
                    print("\n🔔 [ALERT] EVENT DETECTED!")
                    print(f"   Task ID:  {args['taskId']}")
                    print(f"   Employer: {args['employer']}")
                    print(f"   Worker:   {args['worker']}")
                    print(f"   Amount:   {args['amount'] / 10**18} MNEE")
                    
                    if args['worker'] == alice.address:
                        print("   ✅ This job is for ME! (Alice)")
                    else:
                        print("   ❌ This job is for someone else.")

                current_block = latest_block
            
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("\n🛑 Listener stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()