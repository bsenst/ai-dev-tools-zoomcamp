"""Integration test for Homework 3, Question 2.

Start Agent Relay first, then run:
    python q2-agent-relay-integration-test.py

The test talks to the real HTTP API and the server's real database. Set
RELAY_BASE_URL to test another running instance.
"""

import os
import uuid

import httpx


BASE_URL = os.getenv("RELAY_BASE_URL", "http://127.0.0.1:8000") + "/api/v1"


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def register(client, name):
    response = client.post(f"{BASE_URL}/agents", json={"name": name})
    response.raise_for_status()
    return response.json()


def main():
    suffix = uuid.uuid4().hex[:8]
    with httpx.Client() as client:
        sender = register(client, f"q2-sender-{suffix}")
        recipient = register(client, f"q2-recipient-{suffix}")

        task_response = client.post(
            f"{BASE_URL}/tasks",
            headers=auth(sender["token"]),
            json={
                "to": recipient["agent_id"],
                "input": "return the word RELAY",
            },
        )
        task_response.raise_for_status()
        task = task_response.json()
        assert task["status"] == "queued"

        claim_response = client.post(
            f"{BASE_URL}/tasks/claim",
            headers=auth(recipient["token"]),
            json={"worker_id": "q2-integration-test", "wait_seconds": 0},
        )
        claim_response.raise_for_status()
        claim = claim_response.json()
        assert claim["task_id"] == task["task_id"]
        assert claim["input"] == "return the word RELAY"

        complete_response = client.post(
            f"{BASE_URL}/tasks/{task['task_id']}/complete",
            headers=auth(recipient["token"]),
            json={"claim_token": claim["claim_token"], "output": "RELAY"},
        )
        complete_response.raise_for_status()
        assert complete_response.json() == {
            "task_id": task["task_id"],
            "status": "completed",
        }

        sender_view = client.get(
            f"{BASE_URL}/tasks/{task['task_id']}",
            headers=auth(sender["token"]),
        )
        sender_view.raise_for_status()
        result = sender_view.json()
        assert result["status"] == "completed"
        assert result["output"] == "RELAY"

    print("PASS: sender sees completed after recipient submits its result")


if __name__ == "__main__":
    main()
