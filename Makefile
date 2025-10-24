.PHONY: up down api web test fmt lint migrate seed

up:
@docker compose up -d

down:
@docker compose down -v

api:
@cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

web:
@cd frontend && npm run dev

test:
@cd backend && pytest -q
@cd frontend && npm test -- --run

fmt:
@cd backend && ruff check --fix . && black .
@cd frontend && npm run format

lint:
@cd backend && ruff check . && mypy app
@cd frontend && npm run lint

migrate:
@cd backend && alembic upgrade head

seed:
@cd backend && python -m app.scripts.seed_demo
