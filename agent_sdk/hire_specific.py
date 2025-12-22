import sys
from dotenv import load_dotenv
from core import MneeAgent

load_dotenv()
BOB_PK = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"

# Address Book
AGENTS = {
    "alice": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
    "carol": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8", # Warning: This might be Bob's old address in your setup, check below!
    "dave":  "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC"
}

# Carol is actually Account #2. Let's hardcode the correct derived addresses from Anvil default mnemonic
# Account 0: 0xf39... (Alice)
# Account 1: 0x709... (Bob - User) -> WAIT, Carol uses this key in swarm_runner? 
# Let's fix the addresses based on the Keys in swarm_runner.py:

# Alice Key 0xac09... -> Addr 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
# Carol Key 0x5de4... -> Addr 0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC (Account 2)
# Dave  Key 0x7c85... -> Addr 0x90F79bf6EB2c4f870365E785982E1f101E93b906 (Account 3)

AGENTS_CORRECT = {
    "alice": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
    "carol": "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
    "dave":  "0x90F79bf6EB2c4f870365E785982E1f101E93b906"
}

def main():
    if len(sys.argv) < 2:
        print("Usage: python hire_specific.py [alice|carol|dave]")
        return

    target_name = sys.argv[1].lower()
    if target_name not in AGENTS_CORRECT:
        print(f"❌ Unknown agent. Choose: {list(AGENTS_CORRECT.keys())}")
        return

    worker_addr = AGENTS_CORRECT[target_name]
    bob = MneeAgent("Bob", BOB_PK)
    
    print(f"--- 🎯 Hiring {target_name.upper()} ---")
    print(f"Target Address: {worker_addr}")

    # Approve & Hire
    amount = 50 
    wei = bob.w3.to_wei(amount, 'ether')
    
    print("Approving...")
    bob._send_tx(bob.mnee.functions.approve(bob.escrow.address, wei))
    
    print("Depositing to Escrow...")
    bob._send_tx(bob.escrow.functions.createTask(worker_addr, wei))
     
    print("✅ Hired! Watch the Swarm terminal.")

if __name__ == "__main__":
    main()