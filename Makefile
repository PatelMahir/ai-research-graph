.PHONY: help up down logs backend frontend migrate test lint fmt

help:
	@echo "up        - start the full stack (docker compose)"
	@echo "down      - stop and remove containers"
	@echo "logs      - tail all service logs"
	@echo "migrate   - run alembic migrations inside the backend container"
	@echo "test      - run backend + frontend test suites"
	@echo "lint      - run backend (ruff) + frontend (eslint) linters"
	@echo "fmt       - auto-format backend with ruff"

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

migrate:
	docker compose exec backend alembic upgrade head

test:
	cd backend && pytest -q
	cd frontend && npm run typecheck

lint:
	cd backend && ruff check app
	cd frontend && npm run lint

fmt:
	cd backend && ruff format app
