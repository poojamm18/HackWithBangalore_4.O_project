# HackWithBangalore_4.O_project
A Hindsight-powered AI Incident Response Agent that remembers past production incidents, recalls successful and failed resolutions, and improves future troubleshooting recommendations through continuous feedback.

## Streamlit frontend

The original Streamlit IncidentIQ frontend remains in `frontend/` and is
unchanged by the traditional web frontend.

```powershell
python -m pip install -r requirements.txt
python -m streamlit run frontend/app.py
```

### Streamlit demo behavior

- Incident analysis uses transparent, rule-based sample recommendations; it is
  not a live AI analysis.
- Sample incident memories and analytics are labelled as demo data.
- WORKED/FAILED feedback is held only in the current Streamlit session. It is
  not sent to or persisted in Hindsight.
- The service status reports the backend as unconfigured and does not claim a
  successful connection check.

## HTML/CSS/JavaScript frontend

The separate `web/` application uses semantic HTML, CSS, and vanilla JavaScript
modules. It works in demo mode without a backend and does not modify or replace
the Streamlit implementation.

Run a local static server from the repository root:

```powershell
python -m http.server 8000 --directory web
```

Then open <http://localhost:8000>. Serving over HTTP is required for JavaScript
modules; opening `web/index.html` directly as a `file://` URL is not supported.
No npm install or build step is required.

### Theme and demo mode

- Use the sidebar appearance switch to toggle dark/light themes. The selection
  is stored in browser `localStorage` under `incidentiq-theme`.
- The website defaults to demo mode. Sample incident history, memory and
  analytics are marked as demo data; the analysis is rule-based, not live AI.
- WORKED/FAILED demo feedback exists only in the current page session and is
  never reported as saved to Hindsight.
- `web/js/api.js` contains `API_CONFIG`. After the backend contract is
  confirmed, set `mockMode` to `false` and supply `apiBaseUrl` and the confirmed
  relative `endpoints`. Do not put credentials in this browser configuration.

### Web API contract expected by the UI

`web/js/api.js` keeps transport separate from rendering. Route names and
payloads below are the proposed UI-facing contract only; no backend URL or
framework is assumed:

- `analyseIncident(incidentData)`: POST `{description, service, environment,
  severity, logs}`. Expected response: `{incidentId, title, service,
  environment, severity, createdAt, summary, recommendations, memories,
  lessons}`. Each recommendation contains `{id, title, description, steps,
  reason, previousSuccesses, previousFailures, evidenceStatus,
  relatedIncidentIds}`. Each memory contains `{id, title, description, service,
  environment, severity, rootCause, fix, outcome, relevance, createdAt}`.
- `submitFeedback(incidentId, fixId, worked, context)`: POST
  `{incidentId, fixId, worked, context}`. Expected response:
  `{confirmed: boolean, message?: string, simulated?: boolean}`. The backend
  must define what “confirmed” means and whether feedback is durably stored.
- `getIncidentHistory(filters)`: GET with optional `search`, `service`,
  `environment`, `severity`, and `outcome` query parameters. Expected response
  is a list of incident records containing `{id, title, description, service,
  environment, severity, category, rootCause, resolution, outcome, createdAt,
  feedback}`.
- `getMemoryInsights()`: expected response `{counts: {incidentsAnalysed,
  rememberedIncidents, successfulResolutions, failedResolutions},
  commonIncidentTypes, successfulFixes, failurePatterns, lessons}`. List
  entries use `{name, count}`.
- `getServiceStatus()`: expected response
  `{mode, backendConfigured, memoryConfigured, connected, checked, message}`.
  `connected` may be shown only when `checked` is true.

The backend developer still needs to confirm base URL/deployment, routes and
HTTP methods, authentication and CORS policy, request/response field names,
analysis and memory evidence formats, feedback persistence and idempotency,
history filtering/pagination, analytics aggregation, and the health-check
semantics. No endpoint, credential, Hindsight SDK call, or backend framework is
invented here.
