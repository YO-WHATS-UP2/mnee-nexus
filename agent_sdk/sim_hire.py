import os
from dotenv import load_dotenv
from core import MneeAgent

# Anvil Private Keys (Default 0 and 1)
ALICE_PK = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
BOB_PK = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"

def main():
    print("--- Starting MNEE Swarm Simulation ---")
    
    # 1. Initialize Agents
    alice = MneeAgent("Alice (Worker)", ALICE_PK)
    bob = MneeAgent("Bob (Employer)", BOB_PK)

    print(f"Alice Address: {alice.address}")
    print(f"Bob Address:   {bob.address}")
    print("-" * 30)

    # 2. Alice Registers as a Python Dev
    # (She stakes 50 MNEE)
    try:
        alice.register_service("PYTHON_DEV", 100) # 100 MNEE/hr
    except Exception as e:
        print(f"Skip Register: {e} (Maybe already registered?)")

    print("-" * 30)

    # 3. Bob Hires Alice
    # (He pays 100 MNEE into Escrow)
    bob.hire_worker(alice.address, 100)

    print("-" * 30)
    print("🎉 DAY 9 COMPLETE: Python is controlling the Blockchain!")

if __name__ == "__main__":
    main()