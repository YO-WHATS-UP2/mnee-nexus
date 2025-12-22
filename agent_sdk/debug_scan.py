from web3 import Web3

# --- CONFIGURATION ---
RPC_URL = "http://127.0.0.1:8545"

# ⚠️ PASTE YOUR ESCROW ADDRESS HERE
ESCROW_ADDR = "0x5FC8d32690cc91D4c39d9d3abcBD16989F875707" 

# --- SETUP ---
w3 = Web3(Web3.HTTPProvider(RPC_URL))
print(f"🔌 Connected to Anvil? {w3.is_connected()}")
print(f"📦 Current Block Height: {w3.eth.block_number}")

print(f"\n🔎 RAW SCAN of {ESCROW_ADDR}...")

# Ask for ANY log from this address, no matter what it is
logs = w3.eth.get_logs({
    'fromBlock': 0,
    'toBlock': 'latest',
    'address': ESCROW_ADDR
})

if len(logs) == 0:
    print("❌ RESULT: ZERO LOGS.")
    print("   This confirms the contract is empty.")
    print("   The Frontend successfully sent money, but to the WRONG address.")
else:
    print(f"✅ RESULT: FOUND {len(logs)} LOGS!")
    print("   The event IS on the blockchain.")
    print("   The Python Swarm just missed it.")