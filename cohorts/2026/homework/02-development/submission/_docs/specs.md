# Flowboard specification

## Product choice

Flowboard is a mini Kanban board for a small team or an individual. It makes the
current state of work visible without adding project-management ceremony.

## Users and stories

- As a user, I can see tasks grouped into To do, In progress, and Done columns.
- As a user, I can create a task with a title, description, and priority.
- As a user, I can move a task to another column and see the board update immediately.
- As a user, I can delete a task that is no longer relevant.
- As a user, I can refresh the page and keep my tasks because they are stored in SQLite.

## Acceptance criteria

1. The board loads with useful empty states and a clear task count.
2. A title is required and must be between 1 and 120 characters.
3. New tasks start in To do and default to medium priority.
4. Every task can be advanced or moved backward between columns.
5. Changes are persisted by the backend and survive a browser refresh.
6. The interface works at desktop and mobile widths.
7. The API validates input and returns useful HTTP errors.

## Non-goals

- Authentication, multiple boards, comments, file attachments, and due dates.
- Drag-and-drop, notifications, real-time collaboration, and deployment.

## Technical decisions

- The frontend is a Vite vanilla JavaScript application.
- The backend is FastAPI with SQLAlchemy and SQLite.
- `openapi.yaml` is the source of truth for the frontend/backend boundary.
- Backend calls are centralized in `frontend/src/api.js`.