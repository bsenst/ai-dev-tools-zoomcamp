# Homework 4: DevOps and Observability for AI-Built Apps

## Solution Reproduction Scripts

This directory contains Python scripts that reproduce and verify the answers to all 6 questions in Homework 4.

## Files

- `homework4_solution.py` - Main solution script that verifies all 6 questions
- `bug_analysis.py` - Detailed analysis of the express-1002 500 error bug
- `incident-response/` - Incident responder service code (FastAPI app on port 8001)
  - `main.py` - Responder service that receives Grafana alerts and triggers agent
  - `Dockerfile` - Container definition
  - `requirements.txt` - Python dependencies
  - `pyproject.toml` - Project config

## Prerequisites

- Docker with Compose
- Python 3.11+
- `uv` (for tests)

## Setup

1. Clone the Order Tracker starter repository:

```bash
git clone https://github.com/alexeygrigorev/order-tracker.git
cd order-tracker
```

2. Copy the incident-response service into the cloned repo:

```bash
cp -r /workspaces/ai-dev-tools-zoomcamp/cohorts/2026/homework/04-devops/incident-response/ ./incident-response/
```

3. Start the app and responder:

```bash
docker compose up --build -d --wait
```

4. Verify both services are running:

```bash
curl http://localhost:8000/healthz        # Order Tracker app
curl http://localhost:8001/healthz        # Incident responder
```

## Starting the Incident Responder

The incident responder can be started in two ways:

### Option 1: Via Docker Compose (recommended)

The `compose.yaml` in the Order Tracker repo includes a `responder` service. After copying the `incident-response/` directory:

```bash
docker compose up --build -d --wait
```

This starts both the app (port 8000) and the responder (port 8001).

### Option 2: Locally with Python

```bash
cd order-tracker

# Install dependencies
pip install fastapi uvicorn pydantic httpx

# Start the responder
INCIDENT_RESPONSE_PORT=8001 \
APP_DIR=/path/to/order-tracker \
INCIDENTS_DIR=/tmp/incidents \
python3 -m uvicorn incident-response.main:app --host 0.0.0.0 --port 8001
```

### Option 3: Directly with Python

```bash
cd order-tracker/incident-response
python3 main.py
```

## Testing the Responder

Send a test alert to the responder:

```bash
curl -X POST http://localhost:8001/alerts \
  -H 'Content-Type: application/json' \
  -d '{"alerts":[{"status":"firing","labels":{"alertname":"ResponderTest","test":"true"},"annotations":{"summary":"Test notification; no incident to fix"}}]}'
```

View saved incidents:

```bash
curl http://localhost:8001/incidents
```

## Running the Solution Scripts

From the `04-devops` directory:

```bash
# Run the main solution script
python3 homework4_solution.py

# Run the bug analysis script
python3 bug_analysis.py
```

## Answers Summary

### Question 1: What does the health check return?
**Answer:** `{"status":"ok"}`

The `/healthz` endpoint returns a simple JSON status check.

### Question 2: Which HTTP status code does the metric record for this lookup?
**Answer:** `200`

Looking up `standard-1001` returns HTTP 200 (order found).

### Question 3: Which HTTP status code does the metric show in Grafana?
**Answer:** `404`

Looking up `standard-1002` returns HTTP 404 (order not found).

### Question 4: What state does Grafana show for the 5xx alert?
**Answer:** `Normal`

Since `standard-1002` returns 404 (not a 5xx error), the 5xx alert remains in Normal state.

### Question 5: What did the agent respond?
**Answer:** The incident-response service receives the Grafana alert webhook at `POST /alerts` on port 8001. When an alert arrives, it:
1. Saves incident information (endpoint, logs, traces) to `incidents/` directory
2. Starts the coding assistant (kilo) in headless mode to investigate
3. Returns the agent's response

For the test alert `{"alerts":[{"status":"firing","labels":{"alertname":"ResponderTest","test":"true"},"annotations":{"summary":"Test notification; no incident to fix"}}]}`, the responder saves the incident and runs the agent. The agent's response will vary depending on the agent configuration and environment.

### Question 6: What was the problem?
**Answer:** The express delivery date calculation tried to use a day that does not exist in that month.

The `express-1002` order was created with `created_at` set to the last day of the previous month (e.g., August 31). The `order_detail()` function tries to calculate `estimated_delivery` by adding 2 days, resulting in day 33, which doesn't exist in August. This raises a `ValueError` and causes a 500 Internal Server Error.

## Bug Details

From `app/main.py` line 54-60:

```python
def order_detail(row):
    order = as_dict(row)
    if order["priority"] == "express":
        placed_at = datetime.fromisoformat(order["created_at"])
        estimated_at = placed_at.replace(day=placed_at.day + 2)  # BUG HERE
        order["estimated_delivery"] = estimated_at.date().isoformat()
    return order
```

The order `express-1002` is seeded with `created_at` = `previous_month_end` (line 41):

```python
previous_month_end = now.replace(day=1) - timedelta(days=1)
("express-1002", "Sam", "Headphones", "express", "preparing", previous_month_end),
```

When `previous_month_end` is August 31, `placed_at.day + 2` = 33, which is invalid for August.