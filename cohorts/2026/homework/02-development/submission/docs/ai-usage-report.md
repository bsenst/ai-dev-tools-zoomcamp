# AI usage report

I used an AI coding assistant to turn the homework requirements into a small
specification, choose the Flowboard name, draft the OpenAPI contract, and
implement the frontend and backend.

## Verification

- Reviewed the generated API against the acceptance criteria in `_docs/specs.md`.
- Added endpoint tests for validation, persistence, updates, and deletion.
- Built the Vite frontend with `npm run build`.
- Ran the backend tests with `python -m pytest` (or `uv run pytest` in the documented environment).

The final decisions about scope, SQLite persistence, validation behavior, and
the user interface were reviewed and adjusted manually.