# Task Management API

Build a REST API for managing tasks in a team setting.

## Core Requirements

- Users should be able to create, read, update, and delete tasks
- Each task has a title, description, status (todo / in_progress / done), priority (low / medium / high), and an assignee
- Users should be able to list tasks filtered by status or assignee
- The API should return proper HTTP status codes and error messages

## Tech Preferences

- Use Python with FastAPI
- Use SQLite for persistence (no external database setup required)
- Include API documentation (FastAPI auto-generates this, so just make sure it's enabled)

## Bonus

- Add input validation (title required, max 200 chars; description max 2000 chars)
- Write at least a few unit tests for the task creation and filtering logic
