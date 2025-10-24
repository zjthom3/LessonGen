# LessonGen Local Development Runbook

## Prerequisites
- Docker Desktop or Docker Engine 20+
- Python 3.11 with Poetry installed (if running backend outside Docker)
- Node.js 20+

## Environment Setup
1. Copy `.env.sample` to `.env` and adjust secrets as needed.
   - Generate a strong `SECRET_KEY` (e.g., `openssl rand -hex 32`).
   - Provide Google OAuth credentials (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`).
   - Set `VITE_API_BASE_URL` if the API is not running on `http://localhost:8000`.
2. Install backend dependencies with `poetry install` (from `backend/`).
3. Install frontend dependencies with `npm install` (from `frontend/`).

## Running the Stack
```bash
make up
```
- API available at http://localhost:8000
- Frontend available at http://localhost:5173
- pgAdmin at http://localhost:8080 (admin@lessongen.local / lessongen)
- MinIO console at http://localhost:9001 (minioadmin / minioadmin)

Stop the stack and remove volumes:
```bash
make down
```

## Developer Workflow
- Backend development: `make api`
- Frontend development: `make web`
- Run tests: `make test`
- Apply migrations: `make migrate`

## Authentication & Sessions
- The backend exposes `/auth/login`, `/auth/callback`, `/auth/session`, and `/auth/logout`.
- Sessions are cookie-based (`lessongen_session`). Clear the cookie to force logout.
- Optional: restrict Google sign-ins to specific domains via `GOOGLE_ALLOWED_DOMAINS` (comma-separated list).

### Seeding Demo Data
Populate a default tenant, district, school, and sample users:

```bash
cd backend
POETRY_VIRTUALENVS_IN_PROJECT=1 poetry run python -m app.scripts.seed_demo
```

Seeds create:
- Tenant: value from `DEFAULT_TENANT_NAME`
- Admin: `admin@example.edu` (role `admin`)
- Teacher: `teacher@example.edu` (role `teacher`)

## Health Checks
- `GET http://localhost:8000/health` should respond with `{"status": "ok"}`.
- `GET http://localhost:8000/version` returns the running API version.
- `GET http://localhost:8000/lessons` lists lessons for the signed-in user; `POST /lessons`
  creates a new lesson with initial content, and `POST /lessons/{id}/versions` stores a new
  immutable version. All lesson endpoints require an authenticated session cookie.
- `GET http://localhost:8000/lessons/{id}/export?format=pdf|docx|gdoc` downloads the requested
  export. PDF/DOCX responses stream a binary attachment; `format=gdoc` returns a JSON payload that
  can be uploaded manually to Google Docs.
- `POST http://localhost:8000/lms/google-classroom/connect` accepts a stub payload containing
  access/refresh tokens and records a connection. `POST /lms/google-classroom/push` posts an
  assignment record for the most recent lesson version.

## Troubleshooting
- If dependencies are missing in Docker builds, rerun `npm install` or `poetry install` locally
  to refresh lockfiles.
- Ensure no other services are bound to ports 5432, 8000, 5173, 8080, or 9000/9001.
- If Google OAuth redirects fail locally, verify that the redirect URI matches the origin configured in Google Cloud Console and that `FRONTEND_APP_URL` aligns with the frontend dev server.
