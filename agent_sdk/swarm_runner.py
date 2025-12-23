import time
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core import check_for_tasks

# ---------------------------------------------------------
# ⚠️ PASTE YOUR ESCROW ADDRESS HERE (From Step 1)
# ---------------------------------------------------------
ESCROW_ADDRESS = "0xab9270a58bEAC035245059fC7f686DE63e67bC73" # <--- PASTE HERE

def main():
    print(f"\n--- 🐝 MNEE SWARM ACTIVE ---")
    print(f"Listening to Manual Contract: {ESCROW_ADDRESS}")
    print("--------------------------------------------\n")

    if ESCROW_ADDRESS == "0x...":
        print("❌ ERROR: You forgot to paste the Escrow Address in swarm_runner.py!")
        return

    while True:
        try:
            check_for_tasks(ESCROW_ADDRESS)
            time.sleep(2)
        except KeyboardInterrupt:
            print("\n🛑 Swarm Stopped.")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()