from core import MneeAgent
# Alice (Deployer) has all the MNEE initially
alice = MneeAgent("Alice", "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80")
# Bob needs money to hire people
bob_addr = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8" 

print(f"💰 Alice is sending 50,000 MNEE to Bob...")
tx = alice.mnee.functions.transfer(bob_addr, alice.w3.to_wei(50000, 'ether'))
alice._send_tx(tx)
print("✅ Stimulus Complete.")