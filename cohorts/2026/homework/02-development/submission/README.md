# Flowboard

Flowboard is my Homework 2 mini Kanban board: a small full-stack app built
spec-first with a Vite frontend, FastAPI backend, SQLAlchemy, and SQLite.

## Run it

### Backend

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

If `uv` is unavailable, use an activated virtual environment and run
`pip install -e .`, followed by `uvicorn app.main:app --reload --port 8000`.

### Frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite (normally http://localhost:5173). The frontend
uses `http://localhost:8000` for the backend API. To try the original mocked
prototype, run `VITE_USE_MOCKS=true npm run dev`.

## Tests

```bash
cd backend
uv run pytest
```

The tests cover task creation, validation, status updates, deletion, and
persistence through SQLite.

## Homework answers

1. **Project:** Mini Kanban board.
2. **Name:** Flowboard.
3. **Commit SHA:** the SHA of the commit containing this submission.
4. **Frontend command:** `npm run dev` from `frontend/`.
5. **Backend command:** `uv run uvicorn app.main:app --reload --port 8000` from `backend/`.
6. **Backend URL:** `http://localhost:8000` (the frontend API base URL).
7. **Test command:** `uv run pytest` from `backend/`.

## Project map

- `_docs/specs.md` - product specification and acceptance criteria
- `frontend/` - responsive interactive UI and centralized API client
- `backend/` - FastAPI application and SQLAlchemy SQLite store
- `openapi.yaml` - API contract