import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

api_key = os.getenv("HINDSIGHT_API_KEY")
bank_id = os.getenv("HINDSIGHT_BANK_ID", "incident-agent")
if not api_key:
    raise SystemExit("HINDSIGHT_API_KEY is missing from .env")

# Built-in samples, used only if Rohini's file isn't there yet.
SAMPLE = [
    {"id": "INC-042", "title": "Database connection timeout",
     "description": "Payment requests timed out because the database refused new connections.",
     "service": "payments-service", "environment": "Production", "severity": "High",
     "rootCause": "Connection pool saturation", "resolution": "Increase connection pool size",
     "outcome": "Worked", "createdAt": "2026-03-14T10:22:00Z"},
    {"id": "INC-051", "title": "Token validation latency spike",
     "description": "Login checks became slow after the cache nodes ran out of memory.",
     "service": "auth-service", "environment": "Production", "severity": "Medium",
     "rootCause": "Cache nodes out of memory", "resolution": "Restart cache cluster",
     "outcome": "Worked", "createdAt": "2026-04-02T08:10:00Z"},
    {"id": "INC-063", "title": "Queue consumer stalled",
     "description": "Order events stopped being processed in staging.",
     "service": "orders-service", "environment": "Staging", "severity": "Low",
     "rootCause": "Consumers crashed after a bad deploy", "resolution": "Scale consumers",
     "outcome": "Failed", "createdAt": "2026-05-19T15:45:00Z"},
    {"id": "INC-077", "title": "Checkout latency after deploy",
     "description": "Checkout slowed down right after a release.",
     "service": "payments-service", "environment": "Production", "severity": "High",
     "rootCause": "Connection pool saturation", "resolution": "Increase connection pool size",
     "outcome": "Worked", "createdAt": "2026-06-08T12:05:00Z"},
]

# Use Rohini's file if it exists, otherwise the samples above.
data_file = Path(__file__).resolve().parent.parent / "data" / "seed_incidents.json"
if data_file.exists():
    incidents = json.loads(data_file.read_text(encoding="utf-8"))
    print(f"Loaded {len(incidents)} incidents from {data_file.name}")
else:
    incidents = SAMPLE
    print(f"No data/seed_incidents.json yet, using {len(SAMPLE)} built-in samples")

client = Hindsight(base_url="https://api.hindsight.vectorize.io", api_key=api_key)

for i in incidents:
    # Turn each incident into one plain-English note, which is what Hindsight remembers.
    note = (
        f"Incident {i['id']} on {i['service']} ({i['environment']}, severity {i['severity']}): "
        f"{i['title']}. {i['description']} Root cause: {i['rootCause']}. "
        f"Fix tried: {i['resolution']}. Outcome: the fix {i['outcome'].lower()}."
    )
    client.retain(
        bank_id=bank_id,
        content=note,
        context="past incident and its resolution",
        timestamp=i["createdAt"],
    )
    print("Saved", i["id"])
    time.sleep(1)

client.close()
print("Done. Do NOT run this script again, or every incident will be saved twice.")