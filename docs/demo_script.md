# Live Demo Script – AI-Powered Incident Response Agent

**Event:** Hack With Bangalore 4.0  
**Project:** AI-Powered Incident Response Agent  
**Estimated Duration:** 3–4 Minutes

## 1. Introduction (30 Seconds)

Hello everyone!

We have developed an AI-Powered Incident Response Agent that helps engineers troubleshoot technical incidents using historical knowledge and AI-powered recommendations.

Our solution combines Hindsight memory and Groq AI to make incident resolution more informed and efficient.

## 2. Demonstrate the Problem (30 Seconds)

Engineers frequently face recurring technical problems such as database timeouts, API failures and authentication errors.

Often, similar problems have already occurred, but engineers still spend time investigating them again.

Our project addresses this challenge by remembering previous incidents and their resolutions.

## 3. Demonstrate the First Incident (45 Seconds)

Open the application frontend.

Enter the following incident:

**Service:** payments-service

**Environment:** production

**Error:**
Database connection timeout during payment processing.

Click the Analyze button.

Explain:

- The frontend sends the error report to the FastAPI backend.
- Hindsight searches for similar historical incidents.
- Groq AI analyzes the current error and generates troubleshooting recommendations.
- The backend returns the combined results to the frontend.

Show the recalled memory and suggested resolution.

For example, a previous payment database timeout was resolved by increasing the connection pool size after checking database capacity.

## 4. Demonstrate the Second Incident (45 Seconds)

Now submit another similar database timeout incident.

Use a different context:

**Service:** payments-service

**Environment:** production

**Error:**
Database connection timeout during peak traffic. Database connections are already saturated.

Explain that the system can use previous incident experiences to distinguish between similar errors with different underlying causes.

For example, blindly increasing the connection pool previously failed when the database was already overloaded.

The recommendation should consider checking connection usage and query performance before changing pool settings.

## 5. Demonstrate Feedback and Memory (45 Seconds)

Show the feedback options available in the application.

Mark a suggested fix as:

- Worked
- Failed

Explain:

When an engineer submits feedback, the backend retains the incident context and outcome in Hindsight memory.

This information can be recalled during future troubleshooting.

The goal is to avoid repeating unsuccessful approaches and reuse useful previous experiences.

## 6. Explain the Technology (30 Seconds)

Our project uses:

- **FastAPI:** Connects the frontend, memory system and AI model.
- **Hindsight:** Recalls and retains incident knowledge.
- **Groq AI:** Analyzes errors and generates recommendations.
- **HTML, CSS and JavaScript:** Provide the frontend interface.

## 7. Conclusion (20 Seconds)

Our project transforms past incident experiences into reusable technical knowledge.

By combining memory-based recall, AI-powered analysis and engineer feedback, we aim to make troubleshooting faster and more effective.

Thank you!

---

## Important Demo Notes

1. Use simulated incidents from `data/seed_incidents.json`.
2. Confirm that the backend, Hindsight and Groq integrations are working before the presentation.
3. Verify that feedback is actually saved and can be recalled before claiming continuous learning.
4. If live integration is unavailable, clearly identify any mocked results.
5. Do not describe the application as a live production monitoring system.
6. Keep the final recommendations visible so judges can understand the result.

**Expected Demo Duration:** 3–4 minutes.