import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("❌ Error: GEMINI_API_KEY not found in .env file.")
else:
    genai.configure(api_key=API_KEY)
    
    print(f"🔑 Checking models for key: {API_KEY[:5]}...")
    print("\n--- AVAILABLE MODELS ---")
    
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ {m.name}")
    except Exception as e:
        print(f"❌ Error fetching models: {e}")