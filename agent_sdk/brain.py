import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

def perform_task(agent_name, agent_role, task_description):
    """
    Now accepts agent_name and agent_role to customize the AI persona.
    """
    print(f"\n🧠 [{agent_name.upper()} BRAIN] Thinking about: '{task_description}'...")
    
    try:
        # Try the stable model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        You are an autonomous AI agent named {agent_name}.
        Your role/specialty is: {agent_role}.
        
        You have been hired to perform the following task:
        "{task_description}"
        
        Answer specifically from the perspective of a {agent_role}.
        If the task is not related to your role, politely decline or give a generic answer.
        Keep it concise.
        """
        
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        # Fallback
        print(f"⚠️ API Limit/Error: {e}")
        time.sleep(1)
        return f"Task processed by {agent_name} (Backup Mode). Role: {agent_role}."

if __name__ == "__main__":
    print(perform_task("Carol", "Security Auditor", "Check this contract for bugs."))