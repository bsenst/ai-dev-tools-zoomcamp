# Homework 3 Answer Evidence

This folder contains reproducible evidence for the six multiple-choice questions in
[homework.md](homework.md). Questions 1-3 use the real Agent Relay API and database.
Questions 4-6 document the container-orchestration rules used by the requested
Compose, Kubernetes, and CI configurations.

## Prerequisites

- Python 3.11+
- Docker with a running daemon
- A clone of the starter repository:
  `https://github.com/alexeygrigorev/agent-relay`

Install the Python client used by the checks:

```bash
python -m pip install httpx
```

## Question 1: HTTP API and database

**Answer: Agents claim tasks from a DB through an HTTP API.**

Run the source-evidence check:

```bash
python q1-agent-relay-architecture.py
```

It downloads `README.md`, `main.py`, `database.py`, and `storage.py` from the
starter repository and asserts that:

- FastAPI provides the HTTP service.
- SQLite persists the queue and delivery attempts.
- Storage code implements task claiming.

The notebook version is [q1-agent-relay-architecture.ipynb](q1-agent-relay-architecture.ipynb).

## Question 2: Completed task status

**Answer: `completed`.**

Start the starter API from its repository with a fresh database:

```bash
cd /path/to/agent-relay
rm -f agent-relay.db
uvicorn main:app --host 127.0.0.1 --port 8000
```

In another terminal, run the integration test:

```bash
python /path/to/ai-dev-tools-zoomcamp/cohorts/2026/homework/03-deployment/q2-agent-relay-integration-test.py
```

The test registers two agents, submits a task, claims it as the recipient,
submits `RELAY`, and retrieves it as the sender. It asserts that the sender sees
`status == "completed"` and the expected output.

## Question 3: Published Docker port

**Answer: `-p`.**

Copy [Dockerfile.agent-relay](Dockerfile.agent-relay) into the starter repository,
or build with that file as the Dockerfile:

```bash
cd /path/to/agent-relay
docker build -t agent-relay:local \
  -f /path/to/ai-dev-tools-zoomcamp/cohorts/2026/homework/03-deployment/Dockerfile.agent-relay .
docker run --rm --name agent-relay-q3 -p 8000:8000 agent-relay:local
```

The Dockerfile runs Uvicorn with `--host 0.0.0.0`, allowing the published port to
reach the application. In another terminal:

```bash
python /path/to/ai-dev-tools-zoomcamp/cohorts/2026/homework/03-deployment/q3-containerized-task-flow.py
curl -f http://127.0.0.1:8000/
```

The integration check repeats the two-agent flow through the published port.
`-p HOST_PORT:CONTAINER_PORT` publishes a container port to the host. `EXPOSE`
documents a port but does not publish it; `-v` mounts storage; `--name` assigns
a container name.

## Question 4: Docker Compose hostname

**Answer: `postgres`.**

Compose creates a private network and registers each service under its service
name. Given this service:

```yaml
services:
  postgres:
    image: postgres:16
```

the API container must use a database URL whose host is `postgres`, for example:

```text
postgresql+psycopg://relay:relay@postgres:5432/relay
```

`localhost` inside the API container means the API container itself, not the
PostgreSQL container. `host.docker.internal` targets the host machine, and
`0.0.0.0` is a bind address rather than the Compose service name.

## Question 5: Kubernetes replica management

**Answer: `Deployment`.**

A minimal declarative example is:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-relay
spec:
  replicas: 2
  selector:
    matchLabels:
      app: agent-relay
  template:
    metadata:
      labels:
        app: agent-relay
    spec:
      containers:
        - name: api
          image: agent-relay:local
```

The Deployment controller maintains the requested replica count and performs
rolling updates. A Service provides networking, a ConfigMap provides non-secret
configuration, and a Secret stores sensitive configuration.

If `kubectl` is available, validate the resource kind without creating it:

```bash
kubectl explain deployment.spec.replicas
```

## Question 6: Failed-test deployment behavior

**Answer: Keep the existing version running and stop the deployment.**

The CI workflow must put tests before image publishing and deployment. A minimal
workflow shape is:

```yaml
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - run: pytest -q

  deploy:
    needs: verify
    if: ${{ needs.verify.result == 'success' }}
    runs-on: ubuntu-latest
    steps:
      - run: docker build -t agent-relay:${{ github.sha }} .
      - run: kubectl set image deployment/agent-relay api=agent-relay:${{ github.sha }}
```

Because `deploy.needs` depends on `verify`, a failed test prevents the deploy job
from running. The existing Kubernetes Deployment remains running; no new image
is rolled out.
