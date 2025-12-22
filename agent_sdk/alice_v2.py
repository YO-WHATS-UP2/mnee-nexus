import time
import os
from dotenv import load_dotenv
from core import MneeAgent
from brain import perform_task

# Load Env
load_dotenv()
ALICE_PK = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

def main():
    alice = MneeAgent("Alice", ALICE_PK)
    
    print(f"--- 🤖 ALICE V2 (AI-POWERED) IS ONLINE ---")
    print(f"Address: {alice.address}")
    
    # Start listening from the current block
    current_block = alice.w3.eth.block_number
    print(f"Listening for jobs starting at block {current_block}...")

    while True:
        try:
            latest_block = alice.w3.eth.block_number
            
            if latest_block > current_block:
                # Scan new blocks
                print(f".", end="", flush=True) # Heartbeat dot
                
                events = alice.escrow.events.TaskCreated.get_logs(
                    from_block=current_block + 1,
                    to_block=latest_block
                )
                
                for event in events:
                    args = event['args']
                    task_id = args['taskId']
                    employer = args['employer']
                    worker = args['worker']
                    
                    if worker == alice.address:
                        print(f"\n\n🔔 NEW JOB DETECTED! (Task #{task_id})")
                        print(f"   Employer: {employer}")
                        
                        # 1. READ THE JOB (In a real app, description is in IPFS/Database)
                        # For this demo, we will simulate the description based on Task ID
                        # (We pretend Bob sent a description)
                        job_description = "Write a Python function to calculate the Fibonacci sequence."
                        print(f"   📜 Description: {job_description}")
                        
                        # 2. DO THE WORK (AI Brain)
                        print("   🧠 Alice is thinking...")
                        ai_result = perform_task(job_description)
                        print(f"   📝 AI Output:\n{ai_result[:100]}...\n(truncated)")
                        
                        # 3. SUBMIT TO BLOCKCHAIN
                        print("   🔗 Submitting work to chain...")
                        alice.complete_task(task_id)
                        
                        # 4. WAIT & WITHDRAW (The 'Cheating' Fast Forward)
                        print("   ⏰ Fast-forwarding time to get paid...")
                        alice.w3.provider.make_request("evm_increaseTime", [25 * 3600])
                        alice.w3.provider.make_request("evm_mine", [])
                        
                        alice.withdraw_payment(task_id)
                        print("   💰 PAYMENT RECEIVED! Job Done.\n")
                        print("Resuming watch...")

                current_block = latest_block
            
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("\n🛑 Alice signing off.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()