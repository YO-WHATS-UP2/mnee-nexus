import time
from dotenv import load_dotenv
from core import MneeAgent

load_dotenv()
ALICE_PK = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

def main():
    alice = MneeAgent("Alice", ALICE_PK)
    
    # We will assume she works on the most recent Task ID for this demo
    # In a real app, she would read this from the event she just saw.
    task_id = alice.escrow.functions.taskCount().call()
    
    print(f"--- 👷 Alice is Working on Task #{task_id} ---")
    
    # 1. Verify Task Status
    task = alice.escrow.functions.tasks(task_id).call()
    # task struct: (employer, worker, amount, isCompleted, isDisputed, createdAt)
    if task[1] != alice.address:
        print("❌ This task is not for Alice!")
        return
    if task[3] == True:
        print("⚠️ Task already completed.")
        return

    print("running complex_python_analysis.exe ... ⏳")
    time.sleep(2) # Fake work duration
    
    # 2. Submit Work (Complete Task)
    print(f"✅ Work Done! Submitting to Blockchain...")
    alice.complete_task(task_id)
    
    # 3. Check Balance BEFORE Withdraw
    old_bal = alice.mnee.functions.balanceOf(alice.address).call()
    print(f"💰 Balance Before: {alice.w3.from_wei(old_bal, 'ether')} MNEE")

    # 4. FAST FORWARD TIME (The "Wait")
    # In real life, Alice waits 24h. On Anvil, we cheat!
    print("\n⏰ Fast-Forwarding 25 Hours (evm_increaseTime)...")
    alice.w3.provider.make_request("evm_increaseTime", [25 * 3600])
    alice.w3.provider.make_request("evm_mine", []) # Mine a block to confirm time change
    
    # 5. Withdraw
    print("💸 Withdrawing Payment...")
    try:
        alice.withdraw_payment(task_id)
        
        # 6. Verify Wealth
        new_bal = alice.mnee.functions.balanceOf(alice.address).call()
        print(f"💰 Balance After:  {alice.w3.from_wei(new_bal, 'ether')} MNEE")
        print(f"🎉 PROFIT: +{alice.w3.from_wei(new_bal - old_bal, 'ether')} MNEE")
        
    except Exception as e:
        print(f"❌ Withdraw Failed: {e}")

if __name__ == "__main__":
    main()