# Homework 1: AI-Native Developer Workflow

This folder contains a working Django solution for the Household Chores app described in the assignment.

## Question 1: Coding agent

Chosen agent: GitHub Copilot.

## Question 2: Spec (selected features)

The final specification focused on these four features:

1. Add a chore with a title, description, assignee, and due date.
2. Mark chores as complete or incomplete.
3. View all chores in a household dashboard.
4. See which chores are overdue and who is assigned to them.

## GitHub repository

This version is implemented locally in the homework folder and includes a working Django project, backlog, plan, and tests.

## Question 3: Django project

The file that needs to be edited to register the app is:

- `household_chores/settings.py`

This is where the app is added to `INSTALLED_APPS`.

## Question 4: Backlog

Task 1 in the backlog is:

- Create the `Chore` model and wire up the initial Django views/templates.

## Question 5: Start the server

The correct command is:

- `uv run python manage.py runserver`

In this local environment, the equivalent command used is:

- `python manage.py runserver`

## Question 6: Run tests

The correct command is:

- `uv run python manage.py test`

In this local environment, the equivalent command used is:

- `python manage.py test`

## Project structure

- `_docs/plan.md` — product plan and scope
- `backlog.md` — task backlog
- `household_chores/` — Django project settings and URLs
- `chores/` — app with models, views, templates, and tests

## How to run locally

```bash
cd /workspaces/ai-dev-tools-zoomcamp/cohorts/2026/homework/01-ai-native-workflow
python -m pip install django
python manage.py migrate
python manage.py runserver
```

Then open http://127.0.0.1:8000.
