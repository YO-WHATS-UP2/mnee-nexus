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
    {"name": "Carol", "role": "Skeptic",    "pk": REAL_PRIVATE_KEY}, 
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

# --- 🛠️ THE ULTIMATE TOOLBOX ---
class Toolbox:
    @staticmethod
    def get_price(query):
        try:
            print(f"      💰 Checking Price: {query}")
            coin = "bitcoin" if "btc" in query.lower() else "ethereum"
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
            data = requests.get(url, timeout=5).json()
            return f"${data.get(coin, {}).get('usd', 'Unknown')}"
        except: return "Unknown Price"

    @staticmethod
    def search_web(query):
        try:
            print(f"      📡 Searching Web: '{query}'...")
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=1))
                return results[0]['body'] if results else "No info."
        except: return "Search failed."

    @staticmethod
    def generate_image(prompt):
        try:
            print(f"      🎨 Generating Art: '{prompt}'...")
            safe_prompt = prompt.replace(" ", "%20")
            url = f"https://image.pollinations.ai/prompt/{safe_prompt}?nologo=true"
            response = requests.get(url)
            return response.content if response.status_code == 200 else None
        except: return None

    @staticmethod
    def upload_to_pinata(image_bytes, name="art.png"):
        if not PINATA_JWT: return None
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        headers = {"Authorization": f"Bearer {PINATA_JWT}"}
        try:
            print(f"      ☁️ Uploading {name} to IPFS...")
            response = requests.post(url, files={'file': (name, image_bytes)}, headers=headers)
            if response.status_code == 200:
                return f"https://gateway.pinata.cloud/ipfs/{response.json()['IpfsHash']}"
        except: pass
        return None

# --- 🧠 THE AGENT MIND ---
class MneeAgent:
    def __init__(self, name, role, private_key, escrow_address):
        self.name = name
        self.role = role
        self.account = w3.eth.account.from_key(private_key)
        self.address = self.account.address
        self.escrow = w3.eth.contract(address=escrow_address, abi=ESCROW_ABI)

    def think(self, mode):
        print(f"      🧠 {self.name} is starting process [MODE: {mode}]...")
        
        # 🟢 MODE 1: ALICE (Price Check)
        if mode == "RESEARCH":
            price = Toolbox.get_price("ethereum")
            return f"MARKET REPORT: Ethereum is currently trading at {price}. (Verified by Alice)."

        # 🟣 MODE 2: CAROL (Art)
        elif mode == "ART":
            img_bytes = Toolbox.generate_image("Cyberpunk city neon lights futuristic")
            link = Toolbox.upload_to_pinata(img_bytes)
            return f"I have painted this for you: {link}"

        # 🔴 MODE 3: DAVE (THE COUNCIL - TRACK C)
        # The Debate Loop
        elif mode == "COUNCIL":
            print("      👑 THE COUNCIL IS CONVENING (Debate Started)...")
            
            # 1. ALICE (The Bull)
            print("      🗣️ ALICE is speaking...")
            price = Toolbox.get_price("ethereum")
            prompt_alice = f"You are Alice, an optimist. ETH price is {price}. Give 1 short reason why this is good."
            alice_arg = model.generate_content(prompt_alice).text.strip()
            
            # 2. CAROL (The Bear)
            print("      🗣️ CAROL is speaking...")
            news = Toolbox.search_web("Crypto regulatory risks 2024")
            prompt_carol = f"You are Carol, a skeptic. News info: {news}. Critique this argument: '{alice_arg}'. Give 1 short risk."
            carol_arg = model.generate_content(prompt_carol).text.strip()
            
            # 3. DAVE (The Judge)
            print("      ⚖️ DAVE is deciding...")
            prompt_dave = f"Synthesize a verdict. Alice says: {alice_arg}. Carol says: {carol_arg}. Who wins? One sentence."
            verdict = model.generate_content(prompt_dave).text.strip()
            
            # 4. ACTION (The Art of the Deal)
            # Dave commissions a painting based on the verdict
            art_mood = "golden bull run" if "Alice" in verdict or "positive" in verdict else "stormy bear market"
            print(f"      🎨 Commissioning art for mood: {art_mood}")
            img_bytes = Toolbox.generate_image(f"Abstract crypto art representing {art_mood} high quality 8k")
            link = Toolbox.upload_to_pinata(img_bytes, "council_verdict.png")
            
            return f"👑 COUNCIL VERDICT:\n\n📈 ALICE: {alice_arg}\n📉 CAROL: {carol_arg}\n\n⚖️ VERDICT: {verdict}\n\n{link}"

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
        logs = w3.eth.get_logs({'fromBlock': last_checked_block + 1, 'toBlock': current_block, 'address': escrow_address})
    except: return

    for log in logs:
        try:
            # Parse signals based on simple heuristics since we don't have full event decoding here
            data_hex = log['data'].hex().replace("0x", "")
            
            mode = "RESEARCH" # Default
            agent_name = "Alice"
            
            # WAGE DECODER 🕵️‍♂️
            if len(data_hex) >= 64:
                try:
                    amount_int = int(data_hex[-64:], 16)
                    eth_value = float(w3.from_wei(amount_int, 'ether'))
                    
                    if eth_value >= 12.0:
                        mode = "COUNCIL"
                        agent_name = "Dave"
                        print("      🚨 SIGNAL: 12 ETH -> COUNCIL MODE")
                    elif eth_value >= 11.0:
                        mode = "ART"
                        agent_name = "Carol"
                        print("      🚨 SIGNAL: 11 ETH -> ART MODE")
                    elif eth_value >= 10.0:
                        mode = "RESEARCH"
                        agent_name = "Alice"
                        print("      🚨 SIGNAL: 10 ETH -> RESEARCH MODE")
                except: pass

            topics = log['topics']
            if len(topics) >= 2:
                task_id = int(topics[1].hex(), 16)
                print(f"🔎 TASK #{task_id} DETECTED. Executing {agent_name}...")

                agent = MneeAgent(agent_name, "Agent", REAL_PRIVATE_KEY, escrow_address)
                result = agent.think(mode)
                agent.complete_task(task_id, result) 

        except Exception as e:
            continue

    last_checked_block = current_block