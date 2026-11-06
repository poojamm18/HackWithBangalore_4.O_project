import asyncio
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.agent import evidence_status, recommend
from backend.memory import BANK_ID, find_related_ids_async, get_async_client, load_records

load_dotenv()

app = FastAPI(title="Incident Memory Agent")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LIVE_FILE = Path(__file__).resolve().parent.parent / "data" / "live_incidents.json"


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------- Past incidents (Rohini's data file) ----------
def load_incidents():
    """Read the past incidents and shape them the way Pooja's page expects."""
    out = []
    for r in load_records():
        out.append({
            "id": r["id"], "title": r["title"], "description": r["description"],
            "service": r["service"],
            "environment": r["environment"].capitalize(),
            "severity": r["severity"].capitalize(),
            "category": r.get("category") or f"{r['service']} incidents",
            "rootCause": r["rootCause"], "resolution": r["resolution"],
            "outcome": r["outcome"], "createdAt": r["createdAt"],
            "feedback": {}, "recommendations": [], "isDemo": True,
        })
    return out


def load_live():
    """Incidents reported while the app is running (kept across restarts)."""
    if LIVE_FILE.exists():
        try:
            return json.loads(LIVE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def save_live():
    live = [i for i in INCIDENTS if not i["isDemo"]]
    LIVE_FILE.write_text(json.dumps(live, indent=2), encoding="utf-8")


INCIDENTS = load_incidents() + load_live()


def next_incident_id():
    nums = []
    for i in INCIDENTS:
        tail = i["id"].split("-")[-1]
        if tail.isdigit():
            nums.append(int(tail))
    return f"INC-{max(nums + [199]) + 1}"


# ---------- What the frontend sends us ----------
class AnalyzeRequest(BaseModel):
    description: str
    service: str
    environment: str = "Production"
    severity: str = "Medium"
    logs: Optional[str] = ""


class FeedbackRequest(BaseModel):
    incidentId: Optional[str] = None
    fixId: str
    worked: bool
    context: Optional[dict] = None


# ---------- Error format ----------
@app.exception_handler(HTTPException)
async def http_error(request, exc):
    code = "NOT_FOUND" if exc.status_code == 404 else "ERROR"
    return JSONResponse(status_code=exc.status_code,
                        content={"error": {"code": code, "message": str(exc.detail)}})


@app.exception_handler(RequestValidationError)
async def bad_request(request, exc):
    return JSONResponse(status_code=400,
                        content={"error": {"code": "BAD_REQUEST",
                                           "message": "Missing or invalid fields in request"}})


# ---------- 1. Analyse an incident ----------
@app.post("/api/incidents/analyze")
async def analyze(req: AnalyzeRequest):
    incident_id = next_incident_id()
    created = now_iso()
    title = req.description[:60]

    # Only incidents whose outcome is known can teach us anything.
    known = [i for i in INCIDENTS if i["outcome"] in ("Worked", "Failed")]

    # Step 1: ask Hindsight which past incidents look related.
    ids = await find_related_ids_async(req.description, req.service, known)

    # Outcomes engineers reported on this service are always part of the evidence.
    reported = [i["id"] for i in reversed(known)
                if not i["isDemo"] and i["service"] == req.service][:2]
    for rid in reported:
        if rid not in ids:
            ids.append(rid)

    related = [i for i in known if i["id"] in ids]
    related.sort(key=lambda i: ids.index(i["id"]))

    # Step 2: ask Groq to write the recommendations (runs in a side thread).
    result = await asyncio.to_thread(
        recommend, req.description, req.service, req.environment,
        req.severity, req.logs, related,
    )

    memories = [
        {"id": i["id"], "title": i["title"], "description": i["description"],
         "service": i["service"], "environment": i["environment"],
         "severity": i["severity"], "rootCause": i["rootCause"],
         "fix": i["resolution"], "outcome": i["outcome"],
         "relevance": ("Outcome reported by an engineer on an earlier incident."
                       if not i["isDemo"]
                       else "Recalled from team memory as a similar incident.")}
        for i in related
    ]

    # Keep the recommendations with the incident so feedback can find them later.
    INCIDENTS.append({
        "id": incident_id, "title": title, "description": req.description,
        "service": req.service, "environment": req.environment, "severity": req.severity,
        "logs": req.logs, "category": f"{req.service} incidents",
        "rootCause": "Not yet determined", "resolution": "", "outcome": "Pending",
        "createdAt": created, "feedback": {},
        "recommendations": result["recommendations"], "isDemo": False,
    })
    save_live()

    return {
        "incidentId": incident_id, "title": title, "service": req.service,
        "environment": req.environment, "severity": req.severity, "createdAt": created,
        "summary": result["summary"],
        "recommendations": result["recommendations"],
        "memories": memories,
        "lessons": result["lessons"],
    }


# ---------- 2. Record feedback ----------
@app.post("/api/incidents/{incident_id}/feedback")
async def feedback(incident_id: str, req: FeedbackRequest):
    incident = next((i for i in INCIDENTS if i["id"] == incident_id), None)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    rec = next((r for r in incident["recommendations"] if r["id"] == req.fixId), None)
    if rec is None:
        raise HTTPException(status_code=404, detail="Fix not found")

    if req.worked:
        rec["previousSuccesses"] += 1
    else:
        rec["previousFailures"] += 1
    rec["evidenceStatus"] = evidence_status(rec["previousSuccesses"], rec["previousFailures"])

    incident["resolution"] = rec["title"]
    incident["rootCause"] = "Not confirmed (outcome reported by the engineer)"
    incident["outcome"] = "Worked" if req.worked else "Failed"
    incident["feedback"] = {"fixId": req.fixId, "worked": req.worked,
                            "context": req.context or {}}
    save_live()

    # Save the outcome into Hindsight so future recalls can use it.
    note = (
        f"Incident {incident_id} on {incident['service']} "
        f"({incident['environment']}, severity {incident['severity']}): "
        f"{incident['description']} Fix tried: {rec['title']}. {rec['description']} "
        f"Outcome: the fix {'worked' if req.worked else 'failed'}."
    )
    saved = False
    try:
        await get_async_client().aretain(
            bank_id=BANK_ID, content=note,
            context="engineer feedback on a recommended fix",
        )
        saved = True
    except Exception as error:
        print("Hindsight retain failed:", error)

    return {"confirmed": True, "simulated": not saved,
            "message": ("Feedback saved to Hindsight memory." if saved
                        else "Feedback recorded for this session only (Hindsight save failed).")}


# ---------- 3. Incident history (with search and filters) ----------
@app.get("/api/incidents")
def history(search: Optional[str] = None, service: Optional[str] = None,
            environment: Optional[str] = None, severity: Optional[str] = None,
            outcome: Optional[str] = None):
    def match(value, wanted):
        return not wanted or wanted.lower() == "all" or value.lower() == wanted.lower()

    results = []
    for i in INCIDENTS:
        if not (match(i["service"], service) and match(i["environment"], environment)
                and match(i["severity"], severity) and match(i["outcome"], outcome)):
            continue
        if search:
            text = f"{i['title']} {i['description']} {i['service']}".lower()
            if search.lower() not in text:
                continue
        results.append(i)
    return sorted(results, key=lambda i: i["createdAt"], reverse=True)


# ---------- 4. Memory insights ----------
def top(counter):
    return [{"name": n, "count": c} for n, c in counter.most_common(5)]


@app.get("/api/insights")
def insights():
    worked = [i for i in INCIDENTS if i["outcome"] == "Worked"]
    failed = [i for i in INCIDENTS if i["outcome"] == "Failed"]
    return {
        "counts": {
            "incidentsAnalysed": len(INCIDENTS),
            "rememberedIncidents": len(worked) + len(failed),
            "successfulResolutions": len(worked),
            "failedResolutions": len(failed),
        },
        "commonIncidentTypes": top(Counter(i["category"] for i in INCIDENTS)),
        "successfulFixes": top(Counter(i["resolution"] for i in worked)),
        "failurePatterns": top(Counter(i["resolution"] for i in failed)),
        "lessons": ["Check database limits before increasing pool capacity."],
    }


# ---------- 5. Service / connection status ----------
@app.get("/api/services")
def services():
    ready = bool(os.getenv("HINDSIGHT_API_KEY")) and bool(os.getenv("GROQ_API_KEY"))
    return {
        "mode": "live" if ready else "demo",
        "backendConfigured": True,
        "memoryConfigured": bool(os.getenv("HINDSIGHT_API_KEY")),
        "connected": True,
        "checked": True,
        "message": ("Backend connected. Hindsight memory and Groq are configured."
                    if ready else "Backend connected, but API keys are missing."),
    }


# ---------- Serve the frontend folder at / (must be last) ----------
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")