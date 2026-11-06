import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

SEED_FILE = Path(__file__).resolve().parent.parent / "data" / "seed_incidents.json"
BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "incident-demo")

_client = None


def get_client():
    """Connect to Hindsight once and reuse the connection."""
    global _client
    if _client is None:
        key = os.getenv("HINDSIGHT_API_KEY")
        if not key:
            raise RuntimeError("HINDSIGHT_API_KEY is missing from .env")
        _client = Hindsight(base_url="https://api.hindsight.vectorize.io", api_key=key)
    return _client


def load_records():
    """Read Rohini's past incidents from the data folder."""
    return json.loads(SEED_FILE.read_text(encoding="utf-8"))


def recall_texts(description, service):
    """Ask Hindsight what it remembers about a situation like this one."""
    question = (
        f"{service}: {description}. "
        "What similar incidents happened before, and what fixed them?"
    )
    results = get_client().recall(bank_id=BANK_ID, query=question)
    return [r.text for r in results.results]


def find_related_ids(description, service, records, limit=3):
    """Return up to `limit` incident IDs that are related to this incident."""
    known = {r["id"] for r in records}
    ordered = []

    # 1. Memory first: pick out the incident numbers Hindsight mentions.
    try:
        for text in recall_texts(description, service):
            for found in re.findall(r"INC-\d+", text):
                if found in known and found not in ordered:
                    ordered.append(found)
    except Exception as error:
        print("Hindsight recall failed:", error)

    # 2. Top up with other incidents on the same service if we have too few.
    for r in records:
        if len(ordered) >= limit:
            break
        if r["service"] == service and r["id"] not in ordered:
            ordered.append(r["id"])

    return ordered[:limit]


if __name__ == "__main__":
    # Quick test: run this file directly.
    records = load_records()
    description = "Checkout requests are timing out when connecting to the database"
    service = "payments-service"

    texts = recall_texts(description, service)
    print("Hindsight returned", len(texts), "snippets")

    ids = find_related_ids(description, service, records)
    print("Related incident IDs:", ids)
    for r in records:
        if r["id"] in ids:
            print(" ", r["id"], "-", r["title"], "-", r["outcome"])



# ---------- Async version, used by the web server ----------
_async_client = None


def get_async_client():
    global _async_client
    if _async_client is None:
        key = os.getenv("HINDSIGHT_API_KEY")
        if not key:
            raise RuntimeError("HINDSIGHT_API_KEY is missing from .env")
        _async_client = Hindsight(base_url="https://api.hindsight.vectorize.io", api_key=key)
    return _async_client


async def find_related_ids_async(description, service, records, limit=3):
    question = (
        f"{service}: {description}. "
        "What similar incidents happened before, and what fixed them?"
    )
    texts = []
    try:
        results = await get_async_client().arecall(bank_id=BANK_ID, query=question)
        texts = [r.text for r in results.results]
    except Exception as error:
        print("Hindsight recall failed:", error)

    known = {r["id"] for r in records}
    ordered = []
    for text in texts:
        for found in re.findall(r"INC-\d+", text):
            if found in known and found not in ordered:
                ordered.append(found)
    for r in records:
        if len(ordered) >= limit:
            break
        if r["service"] == service and r["id"] not in ordered:
            ordered.append(r["id"])
    return ordered[:limit]