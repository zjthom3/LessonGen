🏁 Project: LessonGen (K–12 Lesson Plan Generator)

Stack: FastAPI (Python) · Postgres · SQLAlchemy + Alembic · React (Vite) · Tailwind · Auth via Google OAuth · Docker Compose
Goal (MVP): Auth → AI lesson generation → Editor/versioning → Standards alignment → Export (PDF/DOCX) → GC/Canvas push (GC only in MVP)

🔧 Pre-Flight (Day 0)

Repo layout

lessongen/
  backend/
    app/ (fastapi)
    migrations/ (alembic)
    tests/
  frontend/
    src/
  infra/
    docker/
    k8s/ (optional later)
  .github/workflows/
  docs/


Core files

README.md, CONTRIBUTING.md, LICENSE

Makefile, .env.sample, .gitignore

pyproject.toml (backend), package.json (frontend)

VS Code: .vscode/settings.json, launch.json, tasks.json

VS Code extensions

Python, Pylance, Ruff, Black Formatter

GitHub Copilot/Chat or ChatGPT – Code Assistant

Docker, Thunder Client/REST Client

ESLint, Prettier

Branch strategy: main (protected), dev, feature branches feat/*

📅 Sprint Plan (6 Sprints, ~1 week each)
Sprint 1 — Foundations & Scaffolding

Theme: Run the stack locally with tests & CI green.

User Stories (from backlog)

Auth & Org scaffolding (Epic 1)

Gen job placeholder (Epic 2.3)

CI/CD guardrails (Epic 8)

Deliverables

Backend

FastAPI app with health endpoints: GET /health, GET /version

SQLAlchemy models for: tenants, districts, schools, users

Alembic baseline migration

JWT session or server-session scaffolding (we’ll swap to Google OAuth in Sprint 2)

Frontend

Vite + React + Tailwind scaffold

Routing (/login, /dashboard, /lessons)

Infra

Docker Compose: api, web, db (Postgres), pgadmin, minio (optional for assets)

GitHub Actions:

python-ci.yml: lint (Ruff), format (Black check), unit tests (pytest), mypy

node-ci.yml: ESLint, typecheck (TS), unit tests (Vitest)

Docs

docs/adr/0001-foundation.md (decisions)

docs/runbook-local.md

Acceptance Criteria

make up brings stack up; make test passes

Hitting http://localhost:5173 shows web shell; http://localhost:8000/health returns 200

CI is green on PR

VS Code Tasks (snippets)

.vscode/tasks.json:

Docker: Up, Docker: Down, API: Dev, Web: Dev, Tests: API, Tests: Web

launch.json:

FastAPI attach debugger, Chrome for frontend

Sprint 2 — Auth, RBAC, Multi-Tenancy

Theme: Real sign-in, users & roles, row-level security patterns.

User Stories

Google OAuth login (Epic 1.1 US-1)

Admin user CRUD (US-2)

Profile & preferences (US-3)

Deliverables

Backend

Google OAuth2 (Authlib) endpoints: /auth/login, /auth/callback, /auth/logout

Session strategy (server-side Redis session or signed cookie)

Models: user_roles

RLS pattern (app-level filters by tenant_id)

Frontend

“Sign in with Google” button; protected routes

Profile page (subjects, grades preferences)

DB

Migrations for new fields

Seed script to create demo tenant/district/school/admin

Tests

Auth flow integration tests (API & UI)

Acceptance Criteria

Sign-in/out works end-to-end; unauthorized routes redirect to /login

Users see only tenant-scoped data

Admin can invite users (email stub) & set roles

Sprint 3 — Lesson Model, Versions, Editor

Theme: Authoring pipeline with immutable versions.

User Stories

Create/edit lesson; autosave; version history (Epic 3.1 US-1/2/3/4)

Lesson library (Epic 3.2 US-1)

Deliverables

Backend

Tables: lessons, lesson_versions, lesson_blocks

Endpoints:

POST /lessons, GET /lessons, GET /lessons/:id

POST /lessons/:id/versions (new version on save)

POST /lessons/:id/restore/:version_no

Frontend

Library grid (filter: subject, grade, tags)

Markdown split editor (left: editor, right: preview) with section tabs

Autosave every 20–30s; “Restore version” action

Docs

Content model diagram; versioning policy

Acceptance Criteria

Create/edit a lesson; autosave creates new version when “Save” hit

Version history lists v1..n; restore sets current_version_id

Library filters work

Sprint 4 — AI Generation & Standards Alignment

Theme: “Generate Lesson” wizard + standards mapping.

User Stories

Lesson creation wizard (Epic 2.1 US-1/2/3)

Auto-suggest standards; manual override (Epic 2.2 US-1/3)

Log AI jobs (Epic 2.3 US-3)

Deliverables

Backend

gen_jobs table + worker (synchronous in MVP; async later)

Endpoint: POST /gen-jobs (inputs: grade, subject, topic, duration, teaching_style, focus_keywords[])

Generation service:

Prompt templates in app/ai/prompts/lesson_v1.md

Calls LLM; writes lesson_versions with structured JSON fields (flow, materials, etc.)

Standards:

Tables: standards_frameworks, standards, lesson_standards

Matching service (keyword/grade/subject filter; simple embedding or rule-based in MVP)

Frontend

Wizard modal → Review screen → “Accept” writes lesson & sets current_version_id

Standards chip list with search/override

Tests

Unit tests for standard matching; e2e for generation happy path

Docs

Prompt v1, red-team notes, guardrails

Acceptance Criteria

From Dashboard, a teacher can generate a complete lesson (Objective, Materials, Flow, Assessment, Differentiation)

Suggested standards appear; teacher can override before save

gen_jobs row created with parameters and result link

Sprint 5 — Export & LMS Push (Google Classroom)

Theme: Get content out where teachers need it.

User Stories

Export PDF/DOCX/Google Doc (Epic 6.2 US-1)

Push to Google Classroom (Epic 6.1 US-1)

Track pushes (Epic 6.1 US-2)

Deliverables

Backend

Export service:

Markdown → PDF (WeasyPrint or Playwright/Puppeteer render)

Markdown → DOCX (python-docx)

Google Docs API create from Markdown (simple styles)

LMS:

lms_connections (Google Classroom OAuth) & lms_pushes

Endpoint: POST /lms/google-classroom/push with payload {course_id, topic_id, due_date}

Frontend

Export menu on lesson: PDF/DOCX/GDoc

Google Classroom “Connect” flow (scopes) + “Assign” modal

Tests

Contract tests for export, mock Google APIs

Docs

Export style guide; GC scopes & troubleshooting

Acceptance Criteria

PDF/DOCX/GDoc export produces readable doc with headers (title, grade, standard)

Teacher can connect Google Classroom and post an assignment; lms_pushes.status shows posted

Sprint 6 — Differentiation, Analytics Lite, Hardening

Theme: Classroom-ready polish + basic insights.

User Stories

Differentiate lesson (ELL/IEP/Gifted) (Epic 5.1 US-1/2)

Basic analytics (Epic 7.1 US-1/2)

Privacy defaults & visibility (Epic 8.1 US-2)

Deliverables

Backend

POST /lessons/:id/differentiate → new version with accommodations/extensions

events + metrics_daily rollup job

Visibility enforcement: private by default; shares table for link sharing

Frontend

“Differentiate” button & selection (ELL/IEP/Gifted)

Dashboard cards: “Lessons generated”, “Exports”, “Time saved” (simple calc)

Share dialog: link with expiration

Quality

Pen tests checklist, rate limit sensitive endpoints, PII audit

Docs

Admin guide; teacher quickstart

Acceptance Criteria

Differentiate flow creates a new version with labeled accommodations

Analytics shows counts for last 30 days

Shared link honors expiration and read-only

🧪 Definition of Ready (DoR)

User story has clear AC, owner, test notes, and mock/UX if UI is involved.

API shape and DB changes reviewed.

Prompts (if any) checked for privacy & style.

✅ Definition of Done (DoD)

Code + tests merged to dev, CI green, review passed.

Docs updated (API, runbook, prompts).

Telemetry events emitted & visible in logs.

Feature behind flag if risky.

🧱 Repo Scaffolding & Commands
Makefile (key targets)
.PHONY: up down api web test fmt lint migrate seed

up:        ## start stack
\tdocker compose up -d

down:      ## stop stack
\tdocker compose down -v

api:       ## run backend dev
\tcd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

web:       ## run frontend dev
\tcd frontend && npm run dev

test:      ## run tests
\tcd backend && pytest -q
\tcd frontend && npm test

fmt:
\tcd backend && ruff check --fix . && black .
\tcd frontend && npm run format

lint:
\tcd backend && ruff check . && mypy app
\tcd frontend && npm run lint

migrate:
\tcd backend && alembic upgrade head

seed:
\tcd backend && python -m app.scripts.seed_demo

.env.sample
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=lessongen
POSTGRES_USER=lessongen
POSTGRES_PASSWORD=lessongen
SECRET_KEY=change_me
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
OPENAI_API_KEY=...
GC_API_SCOPES=https://www.googleapis.com/auth/classroom.courses https://www.googleapis.com/auth/documents

VS Code .vscode/tasks.json (essentials)
{
  "version": "2.0.0",
  "tasks": [
    {"label": "Docker: Up", "type": "shell", "command": "make up"},
    {"label": "API: Dev", "type": "shell", "command": "make api", "problemMatcher": []},
    {"label": "Web: Dev", "type": "shell", "command": "make web", "problemMatcher": []},
    {"label": "Tests: API", "type": "shell", "command": "cd backend && pytest -q"},
    {"label": "Tests: Web", "type": "shell", "command": "cd frontend && npm test"}
  ]
}

🤖 Single Agent Spec (for VS Code Copilot/ChatGPT)
System Prompt (pin this in your VS Code agent)
You are the sole coding agent for LessonGen, a K–12 Lesson Plan Generator.
Constraints:
- Stack: FastAPI, Postgres, SQLAlchemy/Alembic, React (Vite), Tailwind.
- Follow the established data model and endpoints.
- Write production-grade, testable code with docstrings and type hints.
- For each file change, produce: (1) files created/modified with paths, (2) code, (3) test updates, (4) run/verify commands.
- Keep secrets out of code; use .env.
- Prefer small, composable PR-sized changes.
- Emit telemetry via `events` for: auth, lesson_create, gen_job, export, lms_push.
If unsure, propose a minimal interface, then implement it.

Agent Workflows (repeatable prompts)

Scaffold Feature

“Create endpoint POST /gen-jobs with payload {grade, subject, topic, duration, style, focus_keywords[]}; persist to gen_jobs; call openai with prompts/lesson_v1.md; save lesson_versions & link to lesson; return version id. Provide tests & curl examples.”

Build UI Screen

“Implement Lesson Wizard modal: Step 1 inputs, Step 2 preview, Step 3 confirm; integrate /gen-jobs; on confirm write lesson and set current_version_id. Include React tests.”

Standards Matching

“Implement standards suggest service: filter by subject, grade; fuzzy match keywords; return top 5 with scores; unit tests with fixtures.”

Export

“Add export service to convert Markdown → PDF/DOCX (no remote). CLI and API hooks; tests; example files.”

🧰 Test Strategy

Backend: pytest + httpx for API; factory fixtures; coverage ≥ 85% on core modules

Frontend: Vitest + React Testing Library; key flows covered (auth, wizard, editor)

Contract: OpenAPI schema generated; lint with spectral

Playbooks: docs/test-scenarios.md for manual/exploratory tests

📊 Sprint Milestones Summary
Sprint	Milestone	Demo Proof
1	Stack up + CI green	Health endpoint; CI badges
2	Google OAuth + RBAC	Login/out; admin invites
3	Lessons + Versions + Editor	Create/edit/restore
4	AI Gen + Standards	Wizard → Saved lesson with standards
5	Export + GC Push	PDF/DOCX export; Classroom assignment posted
6	Differentiate + Analytics + Hardening	ELL/IEP version; dashboard metrics; link sharing
📦 Backlog to Parking Lot (post-MVP)

Canvas/Schoology connectors

Collaborative editing

Marketplace

Full async workers (Celery/RQ)

Multi-language (fr-CA) generation & UI i18n
