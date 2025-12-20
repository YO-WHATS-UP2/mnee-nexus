import os
import json
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# Constants
RPC_URL = "http://127.0.0.1:8545"
REGISTRY_ADDR = os.getenv("REGISTRY_ADDRESS")
ESCROW_ADDR = os.getenv("ESCROW_ADDRESS")
MNEE_ADDR = "0x8ccedbAe4916b79da7F3F612EfB2EB93A2bFD6cF"

class MneeAgent:
    def __init__(self, name, private_key):
        self.name = name
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
        self.account = self.w3.eth.account.from_key(private_key)
        self.address = self.account.address
        
        # Load ABIs
        self.registry = self._load_contract(REGISTRY_ADDR, "AgentRegistry")
        self.escrow = self._load_contract(ESCROW_ADDR, "TaskEscrow")
        self.mnee = self._load_contract(MNEE_ADDR, "IMNEE") # Uses the interface ABI
        
    def _load_contract(self, address, name):
        # Tries to find the JSON artifact in the 'out' folder
        # Note: IMNEE json might be under out/IMNEE.sol/IMNEE.json
        path_options = [
            f"out/{name}.sol/{name}.json", 
            f"out/{name}.sol/{name}.json" # Fallback if needed
        ]
        
        abi = None
        for path in path_options:
            if os.path.exists(path):
                with open(path, "r") as f:
                    abi = json.load(f)["abi"]
                break
        
        if not abi:
            raise Exception(f"Could not find ABI for {name}")
            
        return self.w3.eth.contract(address=address, abi=abi)

    def _send_tx(self, func_call):
        # Helper to build, sign, and send a transaction
        tx = func_call.build_transaction({
            'from': self.address,
            'nonce': self.w3.eth.get_transaction_count(self.address),
            'gas': 2000000,
            'gasPrice': self.w3.to_wei('5', 'gwei')
        })
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt

    def approve_token(self, spender_addr, amount_ether):
        print(f"[{self.name}] Approving {amount_ether} MNEE to {spender_addr[:6]}...")
        amount_wei = self.w3.to_wei(amount_ether, 'ether')
        self._send_tx(self.mnee.functions.approve(spender_addr, amount_wei))

    def register_service(self, service_tag, rate_ether):
        print(f"[{self.name}] Registering as {service_tag} for {rate_ether} MNEE/hr...")
        
        # 1. Approve Registry to take Stake (50 MNEE)
        self.approve_token(REGISTRY_ADDR, 50)
        
        # 2. Register
        rate_wei = self.w3.to_wei(rate_ether, 'ether')
        self._send_tx(self.registry.functions.registerAgent(service_tag, rate_wei))
        print(f"[{self.name}] ✅ Registration Successful!")

    def hire_worker(self, worker_addr, payment_ether):
        print(f"[{self.name}] Hiring {worker_addr[:6]} for {payment_ether} MNEE...")
        
        # 1. Approve Escrow to take Payment
        self.approve_token(ESCROW_ADDR, payment_ether)
        
        # 2. Create Task
        payment_wei = self.w3.to_wei(payment_ether, 'ether')
        receipt = self._send_tx(self.escrow.functions.createTask(worker_addr, payment_wei))
        
        # Parse Logs to get TaskID (Advanced)
        # For now, we just trust it worked
        print(f"[{self.name}] ✅ Task Created! Transaction Hash: {receipt.transactionHash.hex()}")