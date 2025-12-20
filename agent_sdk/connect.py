import os
import json
from web3 import Web3
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()

RPC_URL = "http://127.0.0.1:8545" # Your local Anvil
REGISTRY_ADDR = os.getenv("REGISTRY_ADDRESS")

def main():
    # 2. Connect to Blockchain
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    if not w3.is_connected():
        print("❌ Failed to connect to Anvil")
        return

    print(f"✅ Connected to Anvil! Block Number: {w3.eth.block_number}")

    # 3. Load the ABI (The interface)
    # Note: We assume you are running this from the project root
    try:
        with open("out/AgentRegistry.sol/AgentRegistry.json", "r") as f:
            registry_json = json.load(f)
            registry_abi = registry_json["abi"]
    except FileNotFoundError:
        print("❌ Could not find ABI file. Are you running from the root folder?")
        return

    # 4. Initialize the Contract
    registry = w3.eth.contract(address=REGISTRY_ADDR, abi=registry_abi)

    # 5. Call a Read Function (Test)
    # Let's try to get the stake amount
    try:
        stake_amount = registry.functions.STAKE_AMOUNT().call()
        print(f"✅ Registry Contact Found!")
        print(f"💰 Stake Requirement: {w3.from_wei(stake_amount, 'ether')} MNEE")
    except Exception as e:
        print(f"❌ Error calling contract: {e}")

if __name__ == "__main__":
    main()