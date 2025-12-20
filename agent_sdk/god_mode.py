import os
from dotenv import load_dotenv
from web3 import Web3
from eth_utils import keccak, to_bytes

load_dotenv()

RPC_URL = "http://127.0.0.1:8545"
MNEE_ADDR = "0x8ccedbAe4916b79da7F3F612EfB2EB93A2bFD6cF"

# Accounts
ALICE = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
BOB = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"

def get_balance_slot(w3, token_addr, user_addr):
    """
    Brute-force checks slots 0-100 to find where the 'balanceOf' mapping lives.
    """
    user_padded = user_addr[2:].zfill(64)
    
    # We want to find the slot where writing a value changes the balance
    for slot_index in range(100):
        slot_padded = hex(slot_index)[2:].zfill(64)
        key = w3.keccak(hexstr=f"{user_padded}{slot_padded}")
        
        # Read current storage at this spot
        data = w3.eth.get_storage_at(token_addr, key)
        
        # It's likely the right slot if it's empty or matches a known balance.
        # Let's try WRITING to it and seeing if balanceOf updates.
        
        # 1. Write a huge number (Test Amount)
        test_amount_hex = "0x" + (64 * "0")[:-len("123")] + "123" # Small identifiable amount
        w3.provider.make_request("anvil_setStorageAt", [token_addr, key.hex(), test_amount_hex])
        
        # 2. Check if the contract thinks the balance changed
        contract_balance = w3.eth.call({
            'to': token_addr,
            'data': '0x70a08231' + user_padded # balanceOf(user)
        })
        
        if int(contract_balance.hex(), 16) == 0x123:
            print(f"✅ Found Balance Mapping at Slot: {slot_index}")
            return slot_index
            
    print("❌ Could not find storage slot.")
    return None

def set_balance(w3, token_addr, user_addr, amount_ether, slot_index):
    # Calculate the exact memory address (key) for this user's balance
    user_padded = user_addr[2:].zfill(64)
    slot_padded = hex(slot_index)[2:].zfill(64)
    key = w3.keccak(hexstr=f"{user_padded}{slot_padded}")
    
    # Format amount as 32-byte hex
    amount_wei = w3.to_wei(amount_ether, 'ether')
    amount_hex = "0x" + hex(amount_wei)[2:].zfill(64)
    
    # Write to Anvil
    w3.provider.make_request("anvil_setStorageAt", [token_addr, key.hex(), amount_hex])
    print(f"💰 Funded {user_addr[:6]} with {amount_ether} MNEE")

def main():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    print(f"--- 🦸 GOD MODE: Forcing Balances ---")
    
    # 1. Find the Slot (Only needs to be done once per token)
    slot = get_balance_slot(w3, MNEE_ADDR, ALICE)
    
    if slot is not None:
        # 2. Fund Alice
        set_balance(w3, MNEE_ADDR, ALICE, 10_000, slot)
        
        # 3. Fund Bob
        set_balance(w3, MNEE_ADDR, BOB, 10_000, slot)
        
        print("\n--- Verification ---")
        # Double check using standard call
        alice_bal = w3.eth.call({'to': MNEE_ADDR, 'data': '0x70a08231' + ALICE[2:].zfill(64)})
        bob_bal = w3.eth.call({'to': MNEE_ADDR, 'data': '0x70a08231' + BOB[2:].zfill(64)})
        
        print(f"Alice Real Balance: {int(alice_bal.hex(), 16) / 1e18}")
        print(f"Bob Real Balance:   {int(bob_bal.hex(), 16) / 1e18}")

if __name__ == "__main__":
    main()