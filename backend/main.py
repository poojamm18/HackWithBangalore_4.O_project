from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="Incident Memory Agent (mock mode)")


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------- Pretend memory (replaced by real Hindsight code later) ----------
INCIDENTS = [
    {"id": "INC-042", "title": "Database connection timeout",
     "description": "Payment requests timing out because the database refused new connections.",
     "service": "payments-service", "environment": "Production", "severity": "High",
     "category": "Database connection exhaustion", "rootCause": "Connection pool saturation",
     "resolution": "Increase connection pool size", "outcome": "Worked",
     "createdAt": "2026-03-14T10:22:00Z", "feedback": {}, "recommendations": [], "isDemo": True},
    {"id": "INC-051", "title": "Token validation latency spike",
     "description": "Login checks became slow after the cache nodes ran out of memory.",
     "service": "auth-service", "environment": "Production", "severity": "Medium",
     "category": "Cache failure", "rootCause": "Cache nodes out of memory",
     "resolution": "Restart cache cluster", "outcome": "Worked",
     "createdAt": "2026-04-02T08:10:00Z", "feedback": {}, "recommendations": [], "isDemo": True},
    {"id": "INC-063", "title": "Queue consumer stalled",
     "description": "Order events stopped being processed in staging.",
     "service": "orders-service", "environment": "Staging", "severity": "Low",
     "category": "Message queue backlog", "rootCause": "Consumers crashed after a bad deploy",
     "resolution": "Scale consumers", "outcome": "Failed",
     "createdAt": "2026-05-19T15:45:00Z", "feedback": {}, "recommendations": [], "isDemo": True},
    {"id": "INC-077", "title": "Checkout latency after deploy",
     "description": "Checkout slowed down right after a release.",
     "service": "payments-service", "environment": "Production", "severity": "High",
     "category": "Database connection exhaustion", "rootCause": "Connection pool saturation",
     "resolution": "Increase connection pool size", "outcome": "Worked",
     "createdAt": "2026-06-08T12:05:00Z", "feedback": {}, "recommendations": [], "isDemo": True},
]

FIXES = {
    "FIX-01": {"title": "Increase connection pool size",
               "description": "Raises the number of database connections the service can open, so requests stop waiting for a free one.",
               "steps": ["Check pool utilisation", "Raise max connections", "Restart workers"],
               "successes": 3, "failures": 1},
    "FIX-02": {"title": "Check database availability and failover",
               "description": "Confirms the database is healthy and switches to a replica if the primary is unreachable.",
               "steps": ["Verify DB health", "Check replica lag", "Fail over if needed"],
               "successes": 1, "failures": 0},
}


def evidence_status(successes, failures):
    if successes == 0 and failures == 0:
        return "No history yet"
    if failures == 0:
        return "Consistently worked"
    if successes == 0:
        return "Previously failed"
    return "Mixed historical outcomes"


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
def analyze(req: AnalyzeRequest):
    incident_id = f"INC-{100 + len(INCIDENTS)}"
    created = now_iso()
    title = req.description[:60]

    # Find earlier incidents on the same service BEFORE saving the new one.
    # (In mock mode, fall back to the first two so the page always has something.)
    same = [i for i in INCIDENTS if i["service"] == req.service] or INCIDENTS[:2]
    memories = [
        {"id": i["id"], "title": i["title"], "description": i["description"],
         "service": i["service"], "environment": i["environment"],
         "severity": i["severity"], "rootCause": i["rootCause"],
         "fix": i["resolution"], "outcome": i["outcome"],
         "relevance": ("An earlier incident on the same service."
                       if i["service"] == req.service
                       else "A similar incident was resolved using this fix.")}
        for i in same[:3]
    ]

    recommendations = []
    for fix_id, f in FIXES.items():
        related_ids = [i["id"] for i in INCIDENTS if i["resolution"] == f["title"]][:3]
        recommendations.append({
            "id": fix_id, "title": f["title"], "description": f["description"],
            "steps": f["steps"],
            "reason": "A similar incident was resolved this way.",
            "previousSuccesses": f["successes"], "previousFailures": f["failures"],
            "evidenceStatus": evidence_status(f["successes"], f["failures"]),
            "relatedIncidentIds": related_ids,
        })

    INCIDENTS.append({
        "id": incident_id, "title": title, "description": req.description,
        "service": req.service, "environment": req.environment, "severity": req.severity,
        "logs": req.logs, "category": "Under investigation",
        "rootCause": "Not yet determined", "resolution": "", "outcome": "Pending",
        "createdAt": created, "feedback": {}, "recommendations": [], "isDemo": False,
    })

    return {
        "incidentId": incident_id, "title": title, "service": req.service,
        "environment": req.environment, "severity": req.severity, "createdAt": created,
        "summary": f"Found {len(memories)} related past incident(s) for {req.service}.",
        "recommendations": recommendations,
        "memories": memories,
        "lessons": ["Check database limits before increasing pool capacity."],
    }


# ---------- 2. Record feedback ----------
@app.post("/api/incidents/{incident_id}/feedback")
def feedback(incident_id: str, req: FeedbackRequest):
    incident = next((i for i in INCIDENTS if i["id"] == incident_id), None)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    fix = FIXES.get(req.fixId)
    if fix is None:
        raise HTTPException(status_code=404, detail="Fix not found")

    if req.worked:
        fix["successes"] += 1
    else:
        fix["failures"] += 1
    incident["resolution"] = fix["title"]
    incident["outcome"] = "Worked" if req.worked else "Failed"
    incident["feedback"] = {"fixId": req.fixId, "worked": req.worked,
                            "context": req.context or {}}
    return {"confirmed": True, "simulated": True,
            "message": "Feedback saved (mock mode, not stored in Hindsight yet)."}


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
    return {
        "mode": "demo",
        "backendConfigured": True,
        "memoryConfigured": False,
        "connected": True,
        "checked": True,
        "message": "Backend connected. Using demo data; Hindsight memory is not connected yet.",
    }

# ---------- Serve the frontend folder at / (must be last) ----------
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")