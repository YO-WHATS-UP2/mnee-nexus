import time
import os
from dotenv import load_dotenv
from core import MneeAgent

# Load Env
load_dotenv()
ALICE_PK = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

def main():
    alice = MneeAgent("Alice", ALICE_PK)
    
    print(f"--- Alice is Polling for Jobs (Address: {alice.address}) ---")
    print(f"Monitoring Escrow Contract: {alice.escrow.address}")

    # 1. Start at the current block
    last_checked_block = alice.w3.eth.block_number
    print(f"Starting at Block: {last_checked_block}")

    while True:
        try:
            # 2. Check current chain tip
            current_block = alice.w3.eth.block_number
            
            # 3. If chain moved forward, scan the new blocks
            if current_block > last_checked_block:
                print(f"Scanning blocks {last_checked_block + 1} to {current_block}...")
                
                # FIX: from_block and to_block (Snake Case)
                events = alice.escrow.events.TaskCreated.get_logs(
                    from_block=last_checked_block + 1,
                    to_block=current_block
                )
                
                for event in events:
                    args = event['args']
                    # Check if Alice is the worker
                    if args['worker'] == alice.address:
                        print("\n🔔 [ALERT] NEW JOB FOUND!")
                        print(f"   Task ID: {args['taskId']}")
                        print(f"   Employer: {args['employer']}")
                        print(f"   Pay:     {args['amount'] / 10**18} MNEE")
                    else:
                        print(f"   (Saw job for someone else: {args['worker']})")

                # Update pointer
                last_checked_block = current_block
            
            time.sleep(1) # Check every second
            
        except KeyboardInterrupt:
            print("\n🛑 Stopping")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()