import json
import os
import re

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
_groq = None


def get_groq():
    """Connect to Groq once and reuse the connection."""
    global _groq
    if _groq is None:
        key = os.getenv("GROQ_API_KEY")
        if not key:
            raise RuntimeError("GROQ_API_KEY is missing from .env")
        _groq = Groq(api_key=key)
    return _groq


def evidence_status(successes, failures):
    if successes == 0 and failures == 0:
        return "No history yet"
    if failures == 0:
        return "Consistently worked"
    if successes == 0:
        return "Previously failed"
    return "Mixed historical outcomes"


def build_prompt(description, service, environment, severity, logs, related):
    lines = []
    for r in related:
        lines.append(
            f"- {r['id']} | {r['service']} | {r['environment']} | severity {r['severity']} | "
            f"outcome: {r['outcome']} | root cause: {r['rootCause']} | fix tried: {r['resolution']}"
        )
    history = "\n".join(lines) or "- (no related past incidents)"
    return f"""You are an incident response assistant for an engineering team.

NEW INCIDENT
Service: {service}
Environment: {environment}
Severity: {severity}
Description: {description}
Logs: {logs or "none provided"}

RELATED PAST INCIDENTS (from the team's memory)
{history}

Recommend up to 3 fixes for the new incident. Rules:
- Prefer fixes that worked in past incidents.
- Every related incident with outcome Failed MUST be covered: put its ID in relatedIncidentIds of a recommendation that says what was tried, why it failed (use only the facts given above) and a safer approach. 
- An incident whose root cause says "Not confirmed" was reported by an engineer on a live incident. Treat its outcome as the newest evidence.
- Use ONLY the incident IDs listed above in relatedIncidentIds. Never invent IDs.
- Each fix needs 2 to 4 short, concrete steps.
- Keep every text field under 40 words.

Reply with ONLY this JSON and nothing else:
{{"summary": "one sentence", "recommendations": [{{"title": "...", "description": "...", "steps": ["..."], "reason": "...", "relatedIncidentIds": ["INC-001"]}}], "lessons": ["..."]}}"""


def parse_json(text):
    """Pull the JSON object out of the model's reply."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("no JSON found in the reply")
    return json.loads(match.group(0))


def ask_groq(prompt):
    response = get_groq().chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return parse_json(response.choices[0].message.content)


def fallback(related):
    """Used when Groq fails: build recommendations straight from the past incidents."""
    recs, seen = [], set()
    for r in related:
        fix = r["resolution"]
        if fix in seen:
            continue
        seen.add(fix)
        ids = [x["id"] for x in related if x["resolution"] == fix]
        recs.append({
            "title": fix[:70],
            "description": fix,
            "steps": [fix],
            "reason": "This was tried in similar past incidents.",
            "relatedIncidentIds": ids,
        })
    return {
        "summary": f"Found {len(related)} related past incident(s).",
        "recommendations": recs[:3],
        "lessons": [],
    }


def finalize(raw, related):
    """Clean up the reply and add the numbers ourselves (never trust the AI to count)."""
    by_id = {r["id"]: r for r in related}
    recs = []
    for n, rec in enumerate(raw.get("recommendations", [])[:3], start=1):
        ids = [i for i in rec.get("relatedIncidentIds", []) if i in by_id]
        successes = sum(1 for i in ids if by_id[i]["outcome"].lower() == "worked")
        failures = sum(1 for i in ids if by_id[i]["outcome"].lower() == "failed")
        recs.append({
            "id": f"FIX-{n:02d}",
            "title": str(rec.get("title", "Suggested fix"))[:100],
            "description": str(rec.get("description", "")),
            "steps": [str(s) for s in (rec.get("steps") or [])][:5],
            "reason": str(rec.get("reason", "")),
            "previousSuccesses": successes,
            "previousFailures": failures,
            "evidenceStatus": evidence_status(successes, failures),
            "relatedIncidentIds": ids,
        })
    return {
        "summary": str(raw.get("summary", "")),
        "recommendations": recs,
        "lessons": [str(x) for x in raw.get("lessons", [])][:3],
    }


def recommend(description, service, environment, severity, logs, related):
    """Main function: Groq advice if possible, fallback if not."""
    try:
        prompt = build_prompt(description, service, environment, severity, logs, related)
        result = finalize(ask_groq(prompt), related)
        if not result["recommendations"]:
            raise ValueError("Groq returned no recommendations")
        return result
    except Exception as error:
        print("Groq failed, using fallback:", error)
        return finalize(fallback(related), related)


if __name__ == "__main__":
    # Quick test: run this file directly.
    from memory import find_related_ids, load_records

    records = load_records()
    description = "Checkout requests are timing out when connecting to the database"
    service = "payments-service"

    ids = find_related_ids(description, service, records)
    related = [r for r in records if r["id"] in ids]
    result = recommend(description, service, "production", "high",
                       "Connection acquisition timed out", related)
    print(json.dumps(result, indent=2))