# Household Chores App Plan

## Goal
Build a simple household chores app that helps a family or roommates track chores, assign them, and keep momentum without confusion.

## Scope

### Core features
1. Create chores with a title, description, assignee, and due date.
2. Mark a chore as complete or still pending.
3. List chores on a single dashboard grouped by status.
4. Highlight overdue tasks and show upcoming items.

### Non-goals for v1
- No user authentication
- No notifications
- No recurring schedules
- No payment or reward system

## UX idea
The home screen shows a board with chores and their assignee, due date, and completion state. The user can quickly update status.

## Technical approach
- Django project for the app shell
- One app: `chores`
- SQLite database for the initial version
- Simple template-based UI
- Django tests covering model and view behavior

## Execution plan
1. Create the Django project and app
2. Model the `Chore` entity
3. Add a basic dashboard view
4. Add form handling for creating chores
5. Test the core flows
6. Run the Django test suite
