"""Reproducible proof for Homework 3, Question 1.

Run with:
    python q1-agent-relay-architecture.py
"""

from urllib.request import urlopen

REPO = "https://raw.githubusercontent.com/alexeygrigorev/agent-relay/main"


def fetch(filename):
    with urlopen(f"{REPO}/{filename}") as response:
        return response.read().decode("utf-8")


readme = fetch("README.md")
main = fetch("main.py")
database = fetch("database.py")
storage = fetch("storage.py")

# Documentation identifies the HTTP service and its persistent queue.
assert "FastAPI service" in readme
assert "SQLite persists the queue and attempts" in readme

# Routes expose agent registration and task lifecycle operations.
assert "FastAPI" in main
assert "/api/v1/agents" in main
assert "claim" in main.lower()
assert "complete" in main.lower() or "result" in main.lower()

# The queue and claim operations are backed by SQLite storage.
assert "sqlalchemy" in database.lower()
assert "sqlite" in database.lower()
assert "claim" in storage.lower()
assert "task" in storage.lower()

print("Evidence verified:")
print("- FastAPI provides the HTTP API.")
print("- SQLite persists the task queue and delivery attempts.")
print("- Storage code implements task claiming.")
print()
print("Answer: Agents claim tasks from a DB through an HTTP API.")
