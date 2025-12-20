import os
from dotenv import load_dotenv
from core import MneeAgent

load_dotenv()

# Keys
ALICE_PK = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
BOB_PK = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"

def check_balance(agent, role):
    print(f"\n--- Checking {role} ({agent.name}) ---")
    print(f"Address: {agent.address}")
    
    # Check ETH (Gas)
    eth_bal = agent.w3.eth.get_balance(agent.address)
    print(f"💰 ETH Balance:  {agent.w3.from_wei(eth_bal, 'ether')}")

    # Check MNEE (Token)
    try:
        mnee_bal = agent.mnee.functions.balanceOf(agent.address).call()
        print(f"💵 MNEE Balance: {agent.w3.from_wei(mnee_bal, 'ether')}")
        
        if role == "Bob":
            # Check Allowance for Escrow
            allowance = agent.mnee.functions.allowance(agent.address, agent.escrow.address).call()
            print(f"🔓 Allowance to Escrow: {agent.w3.from_wei(allowance, 'ether')}")
            
    except Exception as e:
        print(f"❌ Could not read MNEE: {e}")

def main():
    alice = MneeAgent("Alice", ALICE_PK)
    bob = MneeAgent("Bob", BOB_PK)
    
    check_balance(alice, "Alice")
    check_balance(bob, "Bob")

if __name__ == "__main__":
    main()