import time
import json
from web3 import Web3
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION (SEPOLIA) ---
# We use a public node. If it's slow, we might need an Alchemy key later.
ANVIL_RPC = "https://ethereum-sepolia-rpc.publicnode.com"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    model = None

w3 = Web3(Web3.HTTPProvider(ANVIL_RPC))

# --- AGENTS ---
# ⚠️ ON SEPOLIA: We use your funded account for all agents so they can pay gas.
# In a real app, you would send money to each agent individually.
REAL_PRIVATE_KEY = "5b2c402e65767b12f025acd477cc2b87255f08450bd4d4795e0b6d3c9165767f"

AGENTS = [
    {"name": "Alice", "role": "Python Dev", "pk": REAL_PRIVATE_KEY}, 
    {"name": "Carol", "role": "Auditor",    "pk": REAL_PRIVATE_KEY}, 
    {"name": "Dave",  "role": "Analyst",    "pk": REAL_PRIVATE_KEY}  
]

# --- MINIMAL ABI ---
ESCROW_ABI_JSON = """[
    {
        "inputs": [
            {"internalType": "uint256", "name": "taskId", "type": "uint256"},
            {"internalType": "string", "name": "output", "type": "string"} 
        ],
        "name": "completeTask",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]"""
ESCROW_ABI = json.loads(ESCROW_ABI_JSON)

class MneeAgent:
    def __init__(self, name, role, private_key, escrow_address):
        self.name = name
        self.role = role
        self.account = w3.eth.account.from_key(private_key)
        self.address = self.account.address
        self.escrow = w3.eth.contract(address=escrow_address, abi=ESCROW_ABI)

    def think(self, prompt):
        if not model: return "I am thinking... (Gemini is sleeping)"
        try:
            return model.generate_content(f"You are {self.role}. {prompt}").text
        except: return "I am thinking..."

    def complete_task(self, task_id, result_text):
        try:
            print(f"   -> Writing result to blockchain: {result_text[:30]}...")
            # Increased gas limit for public testnet
            tx = self.escrow.functions.completeTask(task_id, result_text).build_transaction({
                'from': self.address, 'nonce': w3.eth.get_transaction_count(self.address),
                'gas': 2000000, 
                'gasPrice': w3.eth.gas_price 
            })
            signed = w3.eth.account.sign_transaction(tx, self.account.key)
            w3.eth.send_raw_transaction(signed.raw_transaction)
            print(f"   -> Tx Sent!")
        except Exception as e:
            print(f"⚠️ Transaction failed: {e}")

# --- STATE MANAGEMENT ---
last_checked_block = 0

def check_for_tasks(escrow_address):
    global last_checked_block
    
    current_block = w3.eth.block_number
    
    if last_checked_block == 0:
        last_checked_block = current_block
        print(f"👀 WATCHING SEPOLIA FOR TASKS starting at Block {current_block}...")
        return

    if current_block <= last_checked_block:
        return

    try:
        logs = w3.eth.get_logs({
            'fromBlock': last_checked_block + 1,
            'toBlock': current_block,
            'address': escrow_address
        })
    except:
        return

    for log in logs:
        try:
            topics = log['topics']
            data_hex = log['data'].hex().replace("0x", "")

            # ADAPTIVE DECODER (Sepolia usually indexes heavily)
            if len(topics) >= 4:
                task_id = int(topics[1].hex(), 16)
                # On Sepolia, we cheat: Check if the worker is OUR address
                # Since all agents share the same key, we just check if it matches the deployer
                worker = w3.to_checksum_address("0x" + topics[3].hex()[-40:])
                amount = int(data_hex, 16) if data_hex else 0
            
            elif len(topics) == 2 and len(data_hex) >= 128:
                task_id = int(topics[1].hex(), 16)
                worker_hex = data_hex[64:128]
                worker = w3.to_checksum_address("0x" + worker_hex[-40:])
                amount = int(data_hex[128:192], 16)
            else:
                continue

            print(f"🔎 [Chain] NEW TASK DETECTED: #{task_id} for {worker}")

            # WAKE AGENT
            # On Sepolia, we only have one active wallet (yours), so we assume ANY
            # task assigned to your wallet is for the active agent.
            my_address = w3.eth.account.from_key(REAL_PRIVATE_KEY).address
            
            if worker.lower() == my_address.lower():
                # For demo purposes, we just wake up Alice
                print(f"⚡ IT'S FOR ME! Waking up...")
                agent = MneeAgent("Alice", "Python Dev", REAL_PRIVATE_KEY, escrow_address)
                
                print(f"🧠 Thinking...")
                result = agent.think(f"Analyze Job #{task_id}.")
                print(f"📝 Output: {result[:50]}...")
                
                agent.complete_task(task_id, result) 
                print(f"✅ Job Complete!\n")

        except Exception as e:
            print(f"Error parsing log: {e}")
            continue

    last_checked_block = current_block