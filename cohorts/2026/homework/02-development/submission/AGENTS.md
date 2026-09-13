# Flowboard agent instructions

- Read `_docs/specs.md` and `openapi.yaml` before changing behavior.
- Keep backend access inside `frontend/src/api.js`; do not scatter `fetch` calls.
- Preserve the three statuses: `todo`, `in_progress`, and `done`.
- Run `cd backend && python -m pytest` after backend changes.
- Run `cd frontend && npm run build` after frontend changes.
- Prefer small, accessible controls and keep the API validation aligned with the spec.