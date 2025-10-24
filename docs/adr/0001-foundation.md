# ADR 0001: Foundational Architecture and Stack

## Status
Accepted – Sprint 1

## Context
LessonGen requires a modern, cloud-friendly architecture that supports rapid iteration on
AI-assisted lesson planning while maintaining a clear separation of concerns between backend,
frontend, and infrastructure concerns. Sprint 1 focuses on delivering a runnable stack with
continuous integration guardrails.

## Decision
- Backend: FastAPI with SQLAlchemy and Alembic for API services, using Postgres as the
  persistent data store.
- Frontend: Vite + React + Tailwind CSS for a type-safe, component-driven web client.
- Infrastructure: Docker Compose for local orchestration of the API, web client, Postgres,
  pgAdmin, and MinIO.
- Tooling: Poetry for backend dependency management, npm for frontend, Ruff/Black/mypy for
  Python quality gates, ESLint/Prettier/Vitest for frontend quality gates.
- Authentication scaffolding relies on JWT tokens; Sprint 2 will replace this with Google
  OAuth.

## Consequences
- Developers can spin up the full stack locally using `make up` and connect to the health
  endpoints for smoke testing.
- CI pipelines enforce linting, formatting, type checks, and unit tests for both backend and
  frontend.
- The schema for tenants, districts, schools, and users is established with a baseline Alembic
  migration.
- Additional services (e.g., AI generation workers) can be layered on in later sprints without
  restructuring the foundation established here.
