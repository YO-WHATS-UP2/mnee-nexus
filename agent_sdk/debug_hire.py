from core import MneeAgent

# Bob's Key
BOB_PK = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
DAVE_ADDR = "0x90F79bf6EB2c4f870365E785982E1f101E93b906"

def main():
    bob = MneeAgent("Bob", BOB_PK)
    amount = 50
    amount_wei = bob.w3.to_wei(amount, 'ether')
    
    print(f"--- 🕵️ FORENSIC ANALYSIS ---")
    print(f"Bob Address:    {bob.address}")
    print(f"Escrow Address: {bob.escrow.address}")
    
    # 1. CHECK BALANCE
    bal = bob.mnee.functions.balanceOf(bob.address).call()
    print(f"💰 Bob's MNEE:    {bob.w3.from_wei(bal, 'ether')}")
    
    if bal < amount_wei:
        print("❌ CRITICAL: Bob is broke! He cannot afford to hire Dave.")
        return

    # 2. CHECK ALLOWANCE
    # Does Escrow have permission to take Bob's money?
    allowance = bob.mnee.functions.allowance(bob.address, bob.escrow.address).call()
    print(f"🔓 Allowance:     {bob.w3.from_wei(allowance, 'ether')}")
    
    if allowance < amount_wei:
        print("⚠️ Allowance too low. Approving now...")
        tx = bob.mnee.functions.approve(bob.escrow.address, amount_wei)
        receipt = bob._send_tx(tx)
        print(f"   ✅ Approval Tx Status: {receipt.status}")
    else:
        print("✅ Allowance is sufficient.")

    # 3. ATTEMPT HIRE (With strict receipt checking)
    print("\n--- 🧨 ATTEMPTING HIRE ---")
    print("Calling createTask()...")
    
    try:
        tx_func = bob.escrow.functions.createTask(DAVE_ADDR, amount_wei)
        
        # We manually build the tx to inspect it
        tx = tx_func.build_transaction({
            'from': bob.address,
            'nonce': bob.w3.eth.get_transaction_count(bob.address),
            'gas': 2000000,
            'gasPrice': bob.w3.to_wei('1', 'gwei')
        })
        
        signed_tx = bob.w3.eth.account.sign_transaction(tx, BOB_PK)
        tx_hash = bob.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"⏳ Tx Sent. Hash: {tx_hash.hex()}")
        
        receipt = bob.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt.status == 1:
            print("🎉 SUCCESS! Status: 1 (Executed)")
        else:
            print("❌ FAILURE! Status: 0 (Reverted)")
            print("   Possible cause: Escrow contract logic failed (e.g., MNEE transfer failed).")

    except Exception as e:
        print(f"❌ Python Error: {e}")

if __name__ == "__main__":
    main()