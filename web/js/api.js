
const API_CONFIG = Object.freeze({
  mockMode: false,
  backendDemoMode: true,
  apiBaseUrl: "http://127.0.0.1:8001",
  endpoints: Object.freeze({
    analyseIncident: "/api/incidents/analyze",
    submitFeedback: "/api/incidents/:incidentId/feedback",
    getIncidentHistory: "/api/incidents",
    getMemoryInsights: "/api/insights",
    getServiceStatus: "/api/services",
  }),
});

export const isDemoMode = () =>
  API_CONFIG.mockMode || API_CONFIG.backendDemoMode;

function ensureRealEndpoint(name, params = {}) {
  let path = API_CONFIG.endpoints[name];

  if (!API_CONFIG.apiBaseUrl || !path) {
    throw new Error(`Backend endpoint "${name}" is not configured.`);
  }

  for (const [key, value] of Object.entries(params)) {
    path = path.replace(`:${key}`, encodeURIComponent(value));
  }

  return `${API_CONFIG.apiBaseUrl.replace(/\/$/, "")}/${path.replace(/^\//, "")}`;
}

async function requestJson(name, options = {}, params = {}) {
  const response = await fetch(ensureRealEndpoint(name, params), {
    ...options,
    headers: {
      Accept: "application/json",
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(
      `Backend request failed (${response.status})${
        detail ? `: ${detail.slice(0, 240)}` : ""
      }`
    );
  }

  return response.json();
}

export async function analyseIncident(incidentData) {
  return requestJson("analyseIncident", {
    method: "POST",
    body: JSON.stringify(incidentData),
  });
}

export async function submitFeedback(
  incidentId,
  fixId,
  worked,
  context = {}
) {
  const payload = { incidentId, fixId, worked, context };

  return requestJson(
    "submitFeedback",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    { incidentId }
  );
}

export async function getIncidentHistory(filters = {}) {
  const query = new URLSearchParams(
    Object.entries(filters).filter(
      ([, value]) => value != null && value !== ""
    )
  );

  const endpoint = ensureRealEndpoint("getIncidentHistory");
  const url = query.size ? `${endpoint}?${query}` : endpoint;

  const response = await fetch(url, {
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new Error(`Backend request failed (${response.status}).`);
  }

  return response.json();
}

export async function getMemoryInsights() {
  return requestJson("getMemoryInsights");
}

export async function getServiceStatus() {
  return requestJson("getServiceStatus");
}
