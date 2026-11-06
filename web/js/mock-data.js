export const demoMemories = [
  {
    id: "DEMO-2041",
    title: "Checkout database pool saturation",
    description: "Connection acquisition timed out during a traffic increase; checkout requests queued.",
    service: "checkout-api",
    environment: "Production",
    severity: "High",
    category: "Database connection exhaustion",
    rootCause: "The connection pool limit was too low for the concurrent workload.",
    fix: "Raised the pool maximum from 20 to 40 and bounded connection wait time.",
    outcome: "Worked",
    relevance: "Both incidents mention database connections and request timeouts.",
    createdAt: "2026-10-28T14:32:00Z",
  },
  {
    id: "DEMO-2038",
    title: "Recurring checkout connection timeout",
    description: "The checkout service returned intermittent connection timeouts after deployment.",
    service: "checkout-api",
    environment: "Staging",
    severity: "Medium",
    category: "Database connection exhaustion",
    rootCause: "The database connection limit was reached under parallel test traffic.",
    fix: "Restarted the service process.",
    outcome: "Failed",
    relevance: "A restart did not resolve a similar connection timeout; inspect pool and database limits.",
    createdAt: "2026-10-17T09:05:00Z",
  },
  {
    id: "DEMO-2031",
    title: "Payments latency from long-running transactions",
    description: "Payment authorization latency rose as database sessions remained busy.",
    service: "payments-api",
    environment: "Production",
    severity: "Critical",
    category: "Database transaction latency",
    rootCause: "Several transactions held connections longer than expected.",
    fix: "Identified and shortened long-running transactions; tuned pool wait limits.",
    outcome: "Worked",
    relevance: "A prior production incident improved after investigating connection usage and long transactions.",
    createdAt: "2026-10-09T18:41:00Z",
  },
  {
    id: "DEMO-2022",
    title: "Catalog API errors after service restart",
    description: "A dependency timeout continued after restarting the API replicas.",
    service: "catalog-api",
    environment: "Production",
    severity: "High",
    category: "Dependency timeout",
    rootCause: "The upstream dependency remained degraded.",
    fix: "Restarted API replicas without checking upstream health.",
    outcome: "Failed",
    relevance: "Restarting the service alone did not fix an upstream dependency issue.",
    createdAt: "2026-09-30T11:18:00Z",
  },
];

export const demoLessons = [
  "Increasing a database connection pool resolved a similar demo incident; verify database limits and workload before adjusting it.",
  "Restarting a service failed to resolve a recurring connection timeout in a demo incident.",
  "A fix worked in staging but failed in production is a scenario to track; validate fixes in the affected environment.",
];

export function createDemoIncident(incidentData) {
  const now = new Date();
  const incidentId = `INC-${crypto.randomUUID().slice(0, 8).toUpperCase()}`;
  const searchText = `${incidentData.description} ${incidentData.logs} ${incidentData.service}`.toLowerCase();
  const databaseIssue = ["database", "connection", "pool", "sql", "timeout"].some((word) => searchText.includes(word));
  const title = incidentData.description.trim().split(/\r?\n/)[0];

  if (!databaseIssue) {
    return {
      incidentId,
      title,
      service: incidentData.service,
      environment: incidentData.environment,
      severity: incidentData.severity,
      createdAt: now.toISOString(),
      summary: "No matching incident pattern was found in the sample memory. Use these general triage prompts to gather evidence before changing production.",
      recommendations: [
        {
          id: `FIX-${crypto.randomUUID().slice(0, 8).toUpperCase()}`,
          title: "Check recent changes and dependency health",
          description: "Compare the incident start time with deployments and inspect upstream health, error rates, and saturation.",
          steps: ["Check recent deploys and configuration changes.", "Review dependency health and service-level metrics.", "Correlate the first error with the incident timeline."],
          reason: "There is no matching demo evidence, so establish the affected component and recent change before applying a fix.",
          previousSuccesses: 0,
          previousFailures: 0,
          evidenceStatus: "Insufficient historical evidence",
          relatedIncidentIds: [],
        },
        {
          id: `FIX-${crypto.randomUUID().slice(0, 8).toUpperCase()}`,
          title: "Capture a bounded diagnostic sample",
          description: "Collect a short, redacted time window of relevant logs and metrics.",
          steps: ["Select a short time window around the onset.", "Remove credentials and personal information.", "Record affected versions and request identifiers where safe."],
          reason: "The sample memory has no verified matching resolution; gather evidence before making a production change.",
          previousSuccesses: 0,
          previousFailures: 0,
          evidenceStatus: "Insufficient historical evidence",
          relatedIncidentIds: [],
        },
      ],
      memories: [],
      lessons: [],
    };
  }

  return {
    incidentId,
    title,
    service: incidentData.service,
    environment: incidentData.environment,
    severity: incidentData.severity,
    createdAt: now.toISOString(),
    summary: "Connection or timeout language detected. This demo triage hint is not a diagnosis; verify against live telemetry.",
    recommendations: [
      {
        id: `FIX-${crypto.randomUUID().slice(0, 8).toUpperCase()}`,
        title: "Inspect connection pool usage and limits",
        description: "Compare active, idle, and waiting connections with database limits; inspect pool wait time and recent traffic.",
        steps: ["Check pool active/idle/waiting counts.", "Compare observed connections with database limits.", "Review wait-time, error-rate, and traffic changes before tuning."],
        reason: "Demo memories include timeouts associated with connection saturation. Check live metrics before changing limits.",
        previousSuccesses: 2,
        previousFailures: 0,
        evidenceStatus: "Previously successful",
        relatedIncidentIds: ["DEMO-2041", "DEMO-2031"],
      },
      {
        id: `FIX-${crypto.randomUUID().slice(0, 8).toUpperCase()}`,
        title: "Avoid relying on a restart as the only fix",
        description: "Before restarting, verify whether the database or upstream dependency remains saturated or degraded.",
        steps: ["Check database and upstream health.", "Inspect whether the same errors remain after a restart.", "Capture diagnostic evidence before clearing state."],
        reason: "In demo history, restarting did not resolve similar connection timeouts or an upstream dependency issue.",
        previousSuccesses: 0,
        previousFailures: 2,
        evidenceStatus: "Previously unsuccessful",
        relatedIncidentIds: ["DEMO-2038", "DEMO-2022"],
      },
      {
        id: `FIX-${crypto.randomUUID().slice(0, 8).toUpperCase()}`,
        title: "Check for long-running transactions",
        description: "Review transaction age, lock waits, and connection hold time for the affected database.",
        steps: ["Inspect transaction age and lock waits.", "Identify connections held longer than expected.", "Validate the suspected cause before tuning pool limits."],
        reason: "A production demo incident improved after long-running transactions were identified; verify this pattern in current telemetry.",
        previousSuccesses: 1,
        previousFailures: 0,
        evidenceStatus: "Previously successful",
        relatedIncidentIds: ["DEMO-2031"],
      },
    ],
    memories: demoMemories.filter((memory) => memory.category.toLowerCase().includes("database") || memory.category.toLowerCase().includes("timeout")),
    lessons: [
      "Increasing a database connection pool resolved a similar demo incident; check database limits and workload before adjusting it.",
      "Restarting a service failed to resolve a recurring connection timeout in demo history.",
      "A production demo incident improved after long-running transactions were identified; verify transaction and lock metrics.",
    ],
  };
}

export function createDemoRecord(incidentData, analysis) {
  return {
    id: analysis.incidentId,
    title: analysis.title,
    description: incidentData.description,
    service: analysis.service,
    environment: analysis.environment,
    severity: analysis.severity,
    category: analysis.summary.includes("Connection or timeout") ? "Database connection exhaustion" : "Unclassified incident",
    rootCause: "Not confirmed",
    resolution: "Recommendations awaiting engineer feedback.",
    outcome: "Pending",
    createdAt: analysis.createdAt,
    feedback: {},
    recommendations: analysis.recommendations,
    isDemo: true,
  };
}
