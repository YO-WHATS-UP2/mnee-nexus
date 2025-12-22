from core import MneeAgent

def main():
    # We use Alice just to read data
    alice = MneeAgent("Alice", "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80")
    
    print(f"--- 🩺 DIAGNOSTIC PROBE ---")
    print(f"Current Block:   {alice.w3.eth.block_number}")
    print(f"Escrow Address:  {alice.escrow.address}")
    
    # 1. Check if the contract exists
    code = alice.w3.eth.get_code(alice.escrow.address)
    if code == b'':
        print("❌ CRITICAL: No Contract found at this address! (Did you update core.py?)")
        return
    else:
        print("✅ Contract Code found.")

    # 2. Check Task Count
    try:
        count = alice.escrow.functions.taskCount().call()
        print(f"📊 Total Tasks in Vault: {count}")
        
        if count == 0:
            print("⚠️ The Vault is EMPTY. The hire transaction never worked.")
        else:
            # 3. Read the last task
            last_task = alice.escrow.functions.tasks(count).call()
            # Struct: (employer, worker, amount, isCompleted, isDisputed, createdAt)
            print(f"\n🕵️ LAST TASK DETAILS (ID #{count}):")
            print(f"   Worker Addr: {last_task[1]}")
            print(f"   Amount:      {alice.w3.from_wei(last_task[2], 'ether')} MNEE")
            print(f"   Completed?   {last_task[3]}")
            
            # Check if it matches Dave
            dave_addr = "0x90F79bf6EB2c4f870365E785982E1f101E93b906"
            if last_task[1] == dave_addr:
                print("✅ MATCH: This task is definitely for DAVE.")
            else:
                print(f"❌ MISMATCH: This task is for {last_task[1]}, not Dave.")

    except Exception as e:
        print(f"❌ Error reading contract: {e}")

if __name__ == "__main__":
    main()