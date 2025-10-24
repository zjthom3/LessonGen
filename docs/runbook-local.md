# LessonGen Local Development Runbook

## Prerequisites
- Docker Desktop or Docker Engine 20+
- Python 3.11 with Poetry installed (if running backend outside Docker)
- Node.js 20+

## Environment Setup
1. Copy `.env.sample` to `.env` and adjust secrets as needed.
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

## Health Checks
- `GET http://localhost:8000/health` should respond with `{"status": "ok"}`.
- `GET http://localhost:8000/version` returns the running API version.

## Troubleshooting
- If dependencies are missing in Docker builds, rerun `npm install` or `poetry install` locally
  to refresh lockfiles.
- Ensure no other services are bound to ports 5432, 8000, 5173, 8080, or 9000/9001.
