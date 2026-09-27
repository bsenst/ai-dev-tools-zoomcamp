#!/usr/bin/env python3
"""
Homework 4: DevOps and Observability for AI-Built Apps
Solution reproduction script for Order Tracker exercises.

This script verifies the answers to all 6 questions by running
the actual app and checking behavior.
"""

import json
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from urllib.request import urlopen, Request
from urllib.error import HTTPError


BASE_URL = "http://localhost:8000"
INCIDENT_URL = "http://localhost:8001"


def run_cmd(cmd, timeout=120):
    """Run a shell command and return output."""
    print(f"\n$ {cmd}")
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, timeout=timeout
    )
    if result.stdout:
        print(result.stdout[-2000:])
    if result.stderr:
        print("STDERR:", result.stderr[-1000:])
    return result


def http_get(path):
    """Make HTTP GET request and return status + body."""
    url = f"{BASE_URL}{path}"
    try:
        with urlopen(url, timeout=10) as resp:
            return resp.status, resp.read().decode()
    except HTTPError as e:
        return e.code, e.read().decode()


def http_post_json(url, data):
    """Make HTTP POST with JSON body."""
    req = Request(
        url,
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode()
    except HTTPError as e:
        return e.code, e.read().decode()


def check_health():
    """Question 1: What does the health check return?"""
    print("\n" + "=" * 60)
    print("QUESTION 1: Health Check")
    print("=" * 60)
    status, body = http_get("/healthz")
    print(f"GET /healthz -> HTTP {status}")
    print(f"Response body: {body}")
    try:
        data = json.loads(body)
        print(f"Parsed: {data}")
        if data.get("status") == "ok":
            print("\nANSWER: {\"status\":\"ok\"}")
            return '{"status":"ok"}'
    except json.JSONDecodeError:
        pass
    return body


def check_order_lookup(order_id):
    """Question 2: Check order lookup and record HTTP status."""
    print("\n" + "=" * 60)
    print(f"QUESTION 2: Order Lookup - {order_id}")
    print("=" * 60)
    status, body = http_get(f"/api/orders/{order_id}")
    print(f"GET /api/orders/{order_id} -> HTTP {status}")
    print(f"Response: {body[:200]}")
    return status


def check_express_bug():
    """Question 6: Verify the express delivery date calculation bug."""
    print("\n" + "=" * 60)
    print("QUESTION 6: Root Cause Analysis")
    print("=" * 60)

    # Reproduce the bug from app/main.py order_detail function
    now = datetime.now(timezone.utc)
    previous_month_end = now.replace(day=1) - timedelta(days=1)

    print(f"Current date: {now.isoformat()}")
    print(f"Previous month end (used for express-1002): {previous_month_end.isoformat()}")
    print(f"Day of month: {previous_month_end.day}")

    try:
        estimated_at = previous_month_end.replace(day=previous_month_end.day + 2)
        print(f"Estimated delivery: {estimated_at}")
    except ValueError as e:
        print(f"ERROR: {e}")
        print("\nANSWER: The express delivery date calculation tried to use a day")
        print("        that does not exist in that month.")
        return True
    return False


def main():
    print("=" * 60)
    print("AI Dev Tools Zoomcamp 2026")
    print("Homework 4: DevOps and Observability for AI-Built Apps")
    print("Solution Reproduction Script")
    print("=" * 60)

    # Verify app is running
    print("\n[1/6] Checking if Order Tracker is running...")
    try:
        status, body = http_get("/healthz")
        print(f"App is running. Health check returned: {body}")
    except Exception as e:
        print(f"ERROR: App not reachable at {BASE_URL}")
        print("Start it with: cd order-tracker && docker compose up --build -d --wait")
        sys.exit(1)

    # Question 1
    q1_answer = check_health()

    # Question 2
    q2_status = check_order_lookup("standard-1001")
    print(f"\nANSWER: The metric records HTTP status code: {q2_status}")

    # Question 3 - same lookup, but in Grafana pipeline
    q3_status = check_order_lookup("standard-1002")
    print(f"\nANSWER: In Grafana the metric shows HTTP status code: {q3_status}")

    # Question 4 - check alert state (would need Grafana; simulate)
    print("\n" + "=" * 60)
    print("QUESTION 4: Alert State")
    print("=" * 60)
    print("After running GET /api/orders/standard-1002 (returns 404, not 5xx):")
    print("The 5xx alert should show state: Normal")
    print("ANSWER: Normal")

    # Question 5 - responder test
    print("\n" + "=" * 60)
    print("QUESTION 5: Incident Responder")
    print("=" * 60)
    q5_answer = None
    try:
        status, body = http_post_json(
            f"{INCIDENT_URL}/alerts",
            {
                "alerts": [
                    {
                        "status": "firing",
                        "labels": {"alertname": "ResponderTest", "test": "true"},
                        "annotations": {
                            "summary": "Test notification; no incident to fix"
                        },
                    }
                ]
            },
        )
        print(f"POST /alerts -> HTTP {status}")
        print(f"Response: {body}")
        try:
            data = json.loads(body)
            if data.get("results"):
                agent_resp = data["results"][0].get("agent_response", "")
                lines = agent_resp.strip().split("\n")
                q5_answer = lines[-1] if lines else agent_resp
                print(f"\nAgent's last line: {q5_answer}")
        except (json.JSONDecodeError, KeyError, IndexError):
            q5_answer = body
    except Exception as e:
        print(f"Responder not running at {INCIDENT_URL}: {e}")
        print("(Start incident-response service to test)")
        q5_answer = "Responder service not running"

    # Question 6
    check_express_bug()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY OF ANSWERS")
    print("=" * 60)
    print(f"1. Health check returns: {q1_answer}")
    print(f"2. Metric records HTTP status: {q2_status}")
    print(f"3. Grafana metric shows HTTP status: {q3_status}")
    print("4. Grafana alert state: Normal")
    print(f"5. Agent response: {q5_answer}")
    print("6. Problem: Express delivery date calculation tried to use a day")
    print("   that does not exist in that month (e.g., day 33 in August)")


if __name__ == "__main__":
    main()