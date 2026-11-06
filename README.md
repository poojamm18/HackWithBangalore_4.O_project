# IncidentIQ — Hindsight-Powered AI Incident Response Agent

IncidentIQ is an AI incident-response agent designed to help engineering teams troubleshoot production incidents by learning from previous incidents, their root causes, and the outcomes of past resolutions.

The goal is to use persistent memory through [Hindsight](https://github.com/vectorize-io/hindsight) to recall relevant incident history, recommend troubleshooting steps, and improve future recommendations using engineer feedback.

## Project Status

**Current implementation:** Traditional HTML, CSS, and JavaScript frontend connected to a FastAPI backend.

**Current operating mode:** Demo mode.

The frontend and backend are connected and the API endpoints have been tested. However, the current backend uses sample incident data and in-memory state. Hindsight persistent memory and live Groq-powered AI analysis are not yet configured.

## Tech Stack

| Component | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, FastAPI |
| API communication | REST API, Fetch |
| AI integration (planned) | Groq |
| Persistent memory (planned) | Hindsight |
| Version control | Git and GitHub |

## Project Structure

```text
HackWithBangalore_4.O_project/
│
├── backend/
│   └── main.py
│
├── web/
│   ├── assets/
│   │   └── incidentiq-mark.svg
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── api.js
│   │   ├── app.js
│   │   ├── mock-data.js
│   │   └── theme.js
│   └── index.html
│
├── .env.example
├── requirements.txt
└── README.md
```

## Features

- **Incident Analysis:** Submit incident descriptions, services, environments, severity levels, and optional logs.
- **Troubleshooting Recommendations:** View suggested fixes, explanations, troubleshooting steps, and available historical evidence.
- **Incident Memory:** Display related historical incidents and their resolution outcomes.
- **Engineer Feedback:** Mark recommendations as WORKED or FAILED.
- **Incident History:** View previously analysed incidents and their outcomes.
- **Memory Insights:** Explore incident patterns, successful resolutions, failure patterns, and lessons.
- **Service Status:** View backend connectivity and memory configuration status.
- **Responsive Interface:** Access the application through a responsive web interface.
- **Theme Switching:** Toggle between light and dark themes.

## Getting Started

### 1. Clone the repository

```powershell
git clone https://github.com/poojamm18/HackWithBangalore_4.O_project.git
cd HackWithBangalore_4.O_project
```

### 2. Install Python dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Start the FastAPI backend

From the project root, run:

```powershell
python -m uvicorn backend.main:app --reload --port 8001
```

The backend will be available at:

- API base URL: http://127.0.0.1:8001
- Interactive API documentation: http://127.0.0.1:8001/docs

### 4. Start the frontend

Open a second terminal in the project root and run:

```powershell
python -m http.server 8000 --directory web
```

Open the application in your browser:

http://127.0.0.1:8000

**Important:** Keep both terminals running while using the application. The frontend communicates with the backend through HTTP requests.

## Backend API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/incidents/analyze` | Analyse a new incident |
| POST | `/api/incidents/{incident_id}/feedback` | Submit feedback on a recommendation |
| GET | `/api/incidents` | Retrieve incident history |
| GET | `/api/insights` | Retrieve incident insights |
| GET | `/api/services` | Retrieve backend and memory status |

The API documentation is available through FastAPI Swagger UI at `/docs`.

## Demo Mode and Current Limitations

The current implementation runs in demo mode.

- Incident analysis uses sample data and rule-based recommendations rather than live AI reasoning.
- Historical incidents and recommendations are based on predefined sample records.
- Feedback is accepted by the backend, but its state is held in memory.
- Feedback and newly analysed incidents can remain visible while the backend process is running, but this state is lost when the backend restarts.
- Hindsight is not yet connected, so incident memories and feedback are not persistently stored.
- Groq-powered AI analysis is not yet enabled.
- The application does not perform live production monitoring, automatically detect incidents, or apply fixes to production systems.

The interface displays demo and configuration status to distinguish the current implementation from the planned AI-powered system.

## Planned AI and Persistent Memory Integration

The next stage of development is to integrate Hindsight and Groq to enable the intended learning workflow.

1. **Incident Analysis:** Use an AI model to understand incoming incident descriptions and technical details.
2. **Memory Retrieval:** Retrieve relevant past incidents and their resolutions using Hindsight.
3. **Recommendation Generation:** Generate troubleshooting recommendations informed by historical successes and failures.
4. **Feedback Collection:** Collect engineer feedback on whether recommended fixes worked.
5. **Memory Retention:** Store incident details, recommendations, and verified outcomes in persistent memory.
6. **Continuous Improvement:** Use recalled outcomes to improve the relevance and reliability of future recommendations.

## Environment Configuration

The repository includes a `.env.example` file containing the configuration variables intended for future integrations:

```env
HINDSIGHT_API_KEY=
HINDSIGHT_BANK_ID=incident-agent
GROQ_API_KEY=
MOCK_MODE=true
```

Copy the example file to `.env` when configuring the integrations.

**Never commit API keys or other secrets to GitHub.**

## Team

Built as a collaborative project for **Hack With Bangalore 4.0**.

---

**IncidentIQ — Turning past incidents into better future responses.**