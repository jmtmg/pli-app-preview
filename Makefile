# PLI — raccourcis dev locaux.
# Testé sous macOS 14 / Linux / Windows + Git Bash.
# Chaque cible suppose que vous êtes à la racine de `pli-app/`.

.PHONY: help install install-be install-fe dev dev-be dev-fe \
        test test-be test-fe test-sec lint lint-be lint-fe typecheck \
        fmt fmt-be fmt-fe clean docker-up docker-down \
        db-migrate db-revision cloud-up cloud-down stripe-listen

help:
	@echo "PLI — cibles disponibles :"
	@echo "  install        installe backend + frontend"
	@echo "  dev            lance backend + frontend en parallèle"
	@echo "  dev-be         backend uniquement (uvicorn --reload)"
	@echo "  dev-fe         frontend uniquement (vite)"
	@echo "  test           exécute les tests des deux côtés"
	@echo "  test-sec       rejoue les tests d'isolation tenant (CI blocker)"
	@echo "  lint           ruff + eslint"
	@echo "  typecheck      mypy + tsc --noEmit"
	@echo "  fmt            ruff format + prettier"
	@echo "  db-migrate     applique les migrations Alembic (mode selon PLI_MODE)"
	@echo "  db-revision m=… crée une nouvelle révision Alembic"
	@echo "  docker-up      docker compose up (profil local, SQLite)"
	@echo "  cloud-up       docker compose --profile cloud up (PG + MinIO + MailHog)"
	@echo "  cloud-down     arrête le stack cloud"
	@echo "  stripe-listen  forward webhooks Stripe → app"
	@echo "  clean          supprime caches + db.sqlite local"

# -------------------------------------------------------------------- install

install: install-be install-fe

install-be:
	cd backend && pip install -e ".[dev]"

install-fe:
	cd frontend && npm install

# -------------------------------------------------------------------- dev

dev:
	@echo ">> Lancement backend :8000 + frontend :5173"
	@$(MAKE) -j2 dev-be dev-fe

dev-be:
	cd backend && uvicorn pli.main:app --reload --host 127.0.0.1 --port 8000

dev-fe:
	cd frontend && npm run dev

# -------------------------------------------------------------------- qa

test: test-be test-fe

test-be:
	cd backend && pytest -q --cov=pli --cov-report=term-missing

test-sec:
	cd backend && pytest tests/test_tenancy_isolation.py -v --no-cov

test-fe:
	cd frontend && npm run test -- --run

lint: lint-be lint-fe

lint-be:
	cd backend && ruff check pli tests

lint-fe:
	cd frontend && npm run lint

typecheck:
	cd backend && mypy pli
	cd frontend && npm run typecheck

fmt: fmt-be fmt-fe

fmt-be:
	cd backend && ruff format pli tests && ruff check --fix pli tests

fmt-fe:
	cd frontend && npm run fmt

# -------------------------------------------------------------------- ops

docker-up:
	docker compose up -d
	@echo ">> Backend  http://localhost:8000"
	@echo ">> Frontend http://localhost:5173"

docker-down:
	docker compose down

cloud-up:
	docker compose --profile cloud up -d
	@echo ">> Cloud backend  http://localhost:8001"
	@echo ">> MinIO console http://localhost:9001 (minioadmin / minioadmin)"
	@echo ">> MailHog UI    http://localhost:8025"

cloud-down:
	docker compose --profile cloud down

stripe-listen:
	stripe listen --forward-to localhost:8001/billing/webhook

db-migrate:
	cd backend && alembic upgrade head

db-revision:
	@[ -n "$(m)" ] || (echo "Usage: make db-revision m='message'" && exit 1)
	cd backend && alembic revision -m "$(m)"

clean:
	rm -rf backend/.pytest_cache backend/.mypy_cache backend/htmlcov backend/.coverage
	rm -rf frontend/node_modules/.vite frontend/dist
	rm -f ~/.pli/db.sqlite
	@echo ">> Caches vidés. La base SQLite locale (~/.pli/db.sqlite) a été supprimée."
