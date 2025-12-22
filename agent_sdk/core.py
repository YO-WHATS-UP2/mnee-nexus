import time
import json
from web3 import Web3
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
ANVIL_RPC = "http://127.0.0.1:8545"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    model = None

w3 = Web3(Web3.HTTPProvider(ANVIL_RPC))

# --- AGENTS ---
AGENTS = [
    {"name": "Alice", "role": "Python Dev", "pk": "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"}, 
    {"name": "Carol", "role": "Auditor",    "pk": "0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a"}, 
    {"name": "Dave",  "role": "Analyst",    "pk": "0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6"}  
]

# --- MINIMAL ABI ---
ESCROW_ABI_JSON = """[
    {
        "inputs": [{"internalType": "uint256", "name": "taskId", "type": "uint256"}],
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

    def complete_task(self, task_id):
        try:
            print(f"   -> Submitting completion for Task {task_id}...")
            tx = self.escrow.functions.completeTask(task_id).build_transaction({
                'from': self.address, 'nonce': w3.eth.get_transaction_count(self.address),
                'gas': 200000, 'gasPrice': w3.to_wei('2', 'gwei')
            })
            signed = w3.eth.account.sign_transaction(tx, self.account.key)
            w3.eth.send_raw_transaction(signed.raw_transaction)
            print(f"   -> Tx Sent!")
        except Exception as e:
            # If it fails, it usually means we already finished it. Safe to ignore.
            pass

# --- STATE MANAGEMENT ---
last_checked_block = 0

def check_for_tasks(escrow_address):
    global last_checked_block
    
    current_block = w3.eth.block_number
    
    # INITIALIZATION:
    # If this is the first run, set the pointer to NOW.
    # This effectively "forgets" all history.
    if last_checked_block == 0:
        last_checked_block = current_block
        print(f"👀 WATCHING FOR NEW TASKS starting at Block {current_block}...")
        return

    # If no new blocks have been mined, do nothing
    if current_block <= last_checked_block:
        return

    # Scan only the NEW blocks
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

            if len(topics) < 2: continue
            
            # --- DECODER ---
            # Topic[1] is Task ID
            task_id = int(topics[1].hex(), 16)

            # Data Chunk 2 is Worker (Chars 64-128)
            if len(data_hex) < 128: continue
            worker_hex = data_hex[64:128]
            worker = w3.to_checksum_address("0x" + worker_hex[-40:])
            
            # Data Chunk 3 is Amount (Chars 128-192)
            amount = 0
            if len(data_hex) >= 192:
                amount = int(data_hex[128:192], 16)

            print(f"🔎 [Chain] NEW TASK DETECTED: #{task_id} for {worker}")

            # WAKE AGENT
            for agent_data in AGENTS:
                agent_addr = w3.eth.account.from_key(agent_data['pk']).address
                
                if agent_addr.lower() == worker.lower():
                    print(f"⚡ {agent_data['name']} MATCHED! Waking up...")
                    agent = MneeAgent(agent_data['name'], agent_data['role'], agent_data['pk'], escrow_address)
                    
                    print(f"🧠 [{agent.name}] Thinking...")
                    result = agent.think(f"Analyze Job #{task_id} with {amount} tokens.")
                    print(f"📝 [{agent.name}] Output: {result[:100]}...")
                    
                    agent.complete_task(task_id)
                    print(f"✅ [{agent.name}] Job Complete!\n")

        except Exception as e:
            continue

    # UPDATE POINTER (Crucial Step!)
    # We move the pointer forward so we never scan these blocks again.
    last_checked_block = current_block