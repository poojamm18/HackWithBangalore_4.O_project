import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

api_key = os.getenv("HINDSIGHT_API_KEY")
bank_id = os.getenv("HINDSIGHT_BANK_ID", "incident-agent")
if not api_key:
    raise SystemExit("HINDSIGHT_API_KEY is missing from .env")

client = Hindsight(base_url="https://api.hindsight.vectorize.io", api_key=api_key)

question = "Database connection timeout on the payments service. What happened before and what fixed it?"
results = client.recall(bank_id=bank_id, query=question)

if not results.results:
    print("Nothing recalled yet. Wait a minute and run again.")
else:
    for r in results.results:
        print("-", r.text)
        print()

client.close()