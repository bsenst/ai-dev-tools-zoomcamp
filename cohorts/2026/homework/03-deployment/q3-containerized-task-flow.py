"""Verify the Q3 task flow against a containerized Agent Relay API.

Build and run the starter first:
    docker build -t agent-relay:local /path/to/agent-relay
    docker run --rm --name agent-relay-q3 -p 8000:8000 agent-relay:local

Then run this script from the course repository. Set RELAY_BASE_URL when the
published host port is different from 8000.
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
        sender = register(client, f"q3-sender-{suffix}")
        recipient = register(client, f"q3-recipient-{suffix}")

        task_response = client.post(
            f"{BASE_URL}/tasks",
            headers=auth(sender["token"]),
            json={"to": recipient["agent_id"], "input": "containerized relay"},
        )
        task_response.raise_for_status()
        task = task_response.json()
        assert task["status"] == "queued"

        claim_response = client.post(
            f"{BASE_URL}/tasks/claim",
            headers=auth(recipient["token"]),
            json={"worker_id": "q3-container-test", "wait_seconds": 0},
        )
        claim_response.raise_for_status()
        claim = claim_response.json()
        assert claim["task_id"] == task["task_id"]

        complete_response = client.post(
            f"{BASE_URL}/tasks/{task['task_id']}/complete",
            headers=auth(recipient["token"]),
            json={
                "claim_token": claim["claim_token"],
                "output": "CONTAINERIZED RELAY",
            },
        )
        complete_response.raise_for_status()

        result_response = client.get(
            f"{BASE_URL}/tasks/{task['task_id']}",
            headers=auth(sender["token"]),
        )
        result_response.raise_for_status()
        result = result_response.json()
        assert result["status"] == "completed"
        assert result["output"] == "CONTAINERIZED RELAY"

    print("PASS: containerized API completed the two-agent task flow")


if __name__ == "__main__":
    main()