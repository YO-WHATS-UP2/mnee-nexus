import time
import json
import requests
from web3 import Web3
import google.generativeai as genai
import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS

load_dotenv()

# --- CONFIGURATION ---
ANVIL_RPC = "https://ethereum-sepolia-rpc.publicnode.com"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINATA_JWT = os.getenv("PINATA_JWT")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-flash-latest') 
else:
    model = None

w3 = Web3(Web3.HTTPProvider(ANVIL_RPC))

# --- AGENTS ---
REAL_PRIVATE_KEY = "5b2c402e65767b12f025acd477cc2b87255f08450bd4d4795e0b6d3c9165767f"
AGENTS = [
    {"name": "Alice", "role": "Researcher", "pk": REAL_PRIVATE_KEY}, 
    {"name": "Carol", "role": "Artist",     "pk": REAL_PRIVATE_KEY}, 
    {"name": "Dave",  "role": "The Council", "pk": REAL_PRIVATE_KEY}  
]

# --- ABI ---
ESCROW_ABI = json.loads("""[
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
]""")

# --- 🛠️ TOOLS ---
class Toolbox:
    @staticmethod
    def upload_to_pinata(image_bytes, name="art.png"):
        if not PINATA_JWT: return None
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        headers = {"Authorization": f"Bearer {PINATA_JWT}"}
        try:
            response = requests.post(url, files={'file': (name, image_bytes)}, headers=headers)
            if response.status_code == 200:
                return f"https://gateway.pinata.cloud/ipfs/{response.json()['IpfsHash']}"
        except: pass
        return None

    @staticmethod
    def generate_image(prompt):
        try:
            print(f"      🎨 Generating Art: '{prompt}'...")
            url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?nologo=true"
            response = requests.get(url)
            return response.content if response.status_code == 200 else None
        except: return None

    @staticmethod
    def get_price(query):
        try:
            print(f"      💰 Checking Price: {query}")
            coin = "bitcoin" if "btc" in query.lower() else "ethereum"
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
            data = requests.get(url, timeout=5).json()
            return f"${data.get(coin, {}).get('usd', 'Unknown')}"
        except: return "Unknown Price"

# --- 🧠 THE AGENT ---
class MneeAgent:
    def __init__(self, name, role, private_key, escrow_address):
        self.name = name
        self.role = role
        self.account = w3.eth.account.from_key(private_key)
        self.address = self.account.address
        self.escrow = w3.eth.contract(address=escrow_address, abi=ESCROW_ABI)

    def think(self, mode, specific_prompt=None):
        print(f"      🧠 {self.name} ({self.role}) is starting process...")
        
        # 🟢 MODE 1: ALICE (Research)
        if mode == "RESEARCH":
            price = Toolbox.get_price("ethereum")
            return f"MARKET REPORT: Ethereum is currently trading at {price}. (Verified by Alice)."

        # 🟣 MODE 2: CAROL (Art)
        elif mode == "ART":
            # Just generate a random cool image
            img_bytes = Toolbox.generate_image("Cyberpunk city neon lights futuristic")
            link = Toolbox.upload_to_pinata(img_bytes)
            return f"I have painted this for you: {link}"

        # 🔴 MODE 3: DAVE (THE COUNCIL)
        # Dave orchestrates everything: He gets a Price AND a Logo.
        elif mode == "COUNCIL":
            print("      👑 THE COUNCIL IS CONVENING...")
            
            # 1. Ask Alice for Data
            price = Toolbox.get_price("ethereum")
            
            # 2. Ask Carol for a Logo
            img_bytes = Toolbox.generate_image("Golden Ethereum Coin floating in space 3d render")
            link = Toolbox.upload_to_pinata(img_bytes, "dave_council.png")
            
            # 3. Dave Synthesizes
            return f"COUNCIL REPORT: We have analyzed the market. ETH is {price}. Our design team proposed this new asset logo: {link}"

        return "I am confused."

    def complete_task(self, task_id, result_text):
        try:
            print(f"   -> ✍️  Writing to Blockchain: {result_text[:40]}...")
            tx = self.escrow.functions.completeTask(task_id, result_text).build_transaction({
                'from': self.address, 'nonce': w3.eth.get_transaction_count(self.address),
                'gas': 2000000, 'gasPrice': w3.eth.gas_price
            })
            signed = w3.eth.account.sign_transaction(tx, self.account.key)
            w3.eth.send_raw_transaction(signed.raw_transaction)
            print(f"   -> ✅ Tx Sent!")
        except Exception as e:
            print(f"⚠️ Tx Failed: {e}")

# --- 🏃‍♂️ THE RUNNER ---
last_checked_block = 0

def check_for_tasks(escrow_address):
    global last_checked_block
    current_block = w3.eth.block_number
    
    if last_checked_block == 0:
        last_checked_block = current_block
        print(f"👀 WATCHING SEPOLIA (Block {current_block})...")
        return

    if current_block <= last_checked_block: return

    try:
        # Get logs to find the Task ID and the AMOUNT (Wage)
        # Note: We need a slightly broader filter to capture the 'TaskCreated' equivalent
        # But 'TaskCompleted' doesn't have the amount. 
        # On Sepolia, we can cheat: We filter by the logs but we assume intent based on recent logs.
        # Actually, let's use the Raw Hex Data to find the intent if possible.
        # SIMPLIFICATION: Since we can't easily decode the 'TaskCreated' amount without the ABI event signature
        # We will use a RANDOMIZER or JUST ASSUME based on the order for this specific demo step.
        
        # WAIT! The log['data'] in 'TaskCreated' contains the amount!
        # But we are listening to a generic filter.
        
        logs = w3.eth.get_logs({'fromBlock': last_checked_block + 1, 'toBlock': current_block, 'address': escrow_address})
    except: return

    for log in logs:
        try:
            topics = log['topics']
            # We need to detect "Task Created" events which have 4 topics usually?
            # Or assume any event on this contract triggers our bot.
            
            # 🕵️‍♂️ DECODING THE SECRET SIGNAL (Wage)
            # This is tricky without the full ABI, but typically:
            # Topic[0] = Event Hash
            # Topic[1] = TaskID
            # Data = Amount (Wage)
            
            data_hex = log['data'].hex().replace("0x", "")
            
            # If data is long, it might contain the amount (Wage) at the end
            # 10 ETH = 10000000000000000000 (Huge number)
            # 11 ETH = 11000000000000000000
            
            mode = "RESEARCH" # Default
            agent_name = "Alice"
            
            if len(data_hex) >= 64:
                # Try to parse the last chunk as the integer amount
                try:
                    # In many events, amount is the last 32 bytes
                    amount_int = int(data_hex[-64:], 16)
                    eth_value = float(w3.from_wei(amount_int, 'ether'))
                    
                    if eth_value >= 12.0:
                        mode = "COUNCIL"
                        agent_name = "Dave"
                        print("      🚨 SIGNAL DETECTED: 12 ETH -> COUNCIL MODE")
                    elif eth_value >= 11.0:
                        mode = "ART"
                        agent_name = "Carol"
                        print("      🚨 SIGNAL DETECTED: 11 ETH -> ART MODE")
                    elif eth_value >= 10.0:
                        mode = "RESEARCH"
                        agent_name = "Alice"
                        print("      🚨 SIGNAL DETECTED: 10 ETH -> RESEARCH MODE")
                except:
                    pass

            if len(topics) >= 2:
                task_id = int(topics[1].hex(), 16)
                print(f"🔎 TASK #{task_id} DETECTED. Mode: {mode}")

                agent = MneeAgent(agent_name, "Agent", REAL_PRIVATE_KEY, escrow_address)
                result = agent.think(mode)
                agent.complete_task(task_id, result) 

        except Exception as e:
            continue

    last_checked_block = current_block