# PLI — raccourcis dev locaux.
# Testé sous macOS 14 / Linux / Windows + Git Bash.
# Chaque cible suppose que vous êtes à la racine de `pli-app/`.

.PHONY: help install install-be install-fe dev dev-be dev-fe demo \
        test test-be test-be-all test-be-future test-fe test-sec lint lint-be lint-fe typecheck typecheck-all typecheck-future \
        fmt fmt-be fmt-fe clean docker-up docker-down \
        db-migrate db-revision cloud-up cloud-down stripe-listen

help:
	@echo "PLI — cibles disponibles :"
	@echo "  install        installe backend + frontend"
	@echo "  dev            lance backend + frontend en parallèle"
	@echo "  dev-be         backend uniquement (uvicorn --reload)"
	@echo "  dev-fe         frontend uniquement (vite)"
	@echo "  demo           lance backend demo + frontend"
	@echo "  test           exécute les tests MVP des deux côtés"
	@echo "  test-sec       rejoue les tests d'isolation tenant (CI blocker historique)"
	@echo "  test-be-future rejoue les strates backend futures isolées (doit échouer tant que non intégrées)"
	@echo "  lint           ruff MVP + ESLint 9 flat config + tsc --noEmit"
	@echo "  typecheck      mypy MVP + tsc --noEmit"
	@echo "  typecheck-all  mypy backend complet + tsc --noEmit (historique, non vert tant que M2-M4 non intégrés)"
	@echo "  typecheck-future mypy des modules backend futurs isolés"
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
	cd backend && $(BACKEND_PY) -m uvicorn pli.main:app --reload --host 127.0.0.1 --port 8000

dev-fe:
	cd frontend && npm run dev

demo:
	@echo ">> Lancement demo locale: backend :8000 + frontend :5173"
	@PLI_DEMO=true PLI_DB_PATH=$$(pwd)/.pli-dev/db.sqlite PLI_ATTACHMENTS_DIR=$$(pwd)/.pli-dev/att $(MAKE) -j2 dev-be dev-fe

# -------------------------------------------------------------------- qa

BACKEND_PY ?= .venv/bin/python

test: test-be test-fe

BACKEND_MVP_TESTS := \
	tests/test_demo_mvp.py \
	tests/test_local_demo.py \
	tests/test_db_schema.py \
	tests/test_parser.py \
	tests/test_accounts.py \
	tests/test_contacts.py \
	tests/test_conversations.py \
	tests/test_messages.py \
	tests/test_drafts.py \
	tests/test_health_logging.py \
	tests/test_storage_adapters.py \
	tests/test_sync_gmail.py \
	tests/test_licensing.py \
	tests/test_emails.py

BACKEND_MVP_LINT_TARGETS := pli tests/test_demo_mvp.py tests/test_local_demo.py tests/test_drafts.py

BACKEND_MVP_TYPECHECK_TARGETS := \
	pli/config.py \
	pli/db.py \
	pli/demo.py \
	pli/api/accounts.py \
	pli/api/contacts.py \
	pli/api/conversations.py \
	pli/api/messages.py \
	pli/api/search.py \
	pli/api/demo.py

# Strates récupérées M2-M4 non intégrées au runtime local MVP.
# Ces commandes gardent le signal historique reproductible sans les faire
# passer pour des gates du produit local fonctionnel.
BACKEND_FUTURE_TESTS := \
	tests/test_auth_flow.py \
	tests/test_auth_oauth.py \
	tests/test_tenancy_isolation.py \
	tests/test_api_feedback.py \
	tests/test_stripe_webhooks.py \
	tests/test_beta_activation.py \
	tests/test_beta_batches.py \
	tests/test_beta_nps.py \
	tests/test_gdpr.py \
	tests/unit/ocr/test_worker.py \
	tests/integration/ocr/test_api.py

BACKEND_FUTURE_TYPECHECK_TARGETS := \
	pli/auth \
	pli/beta \
	pli/billing \
	pli/gdpr \
	pli/ocr \
	pli/providers \
	pli/tenancy \
	pli/api/auth.py \
	pli/api/auth_pli.py \
	pli/api/billing.py \
	pli/api/feedback.py \
	pli/api/invitations.py \
	pli/api/licensing.py \
	pli/api/waitlist.py \
	pli/crypto/attachments.py \
	pli/crypto/backups.py

test-be:
	cd backend && $(BACKEND_PY) -m pytest -q --no-cov $(BACKEND_MVP_TESTS)

test-be-all:
	cd backend && $(BACKEND_PY) -m pytest -q --no-cov

test-be-future:
	cd backend && $(BACKEND_PY) -m pytest -q --no-cov $(BACKEND_FUTURE_TESTS)

test-sec:
	cd backend && $(BACKEND_PY) -m pytest tests/test_tenancy_isolation.py -v --no-cov

test-fe:
	cd frontend && npm run test -- --run

lint: lint-be lint-fe

lint-be:
	cd backend && $(BACKEND_PY) -m ruff check $(BACKEND_MVP_LINT_TARGETS)

lint-fe:
	cd frontend && npm run lint

typecheck:
	cd backend && $(BACKEND_PY) -m mypy $(BACKEND_MVP_TYPECHECK_TARGETS)
	cd frontend && npm run type-check

typecheck-all:
	cd backend && $(BACKEND_PY) -m mypy pli
	cd frontend && npm run type-check

typecheck-future:
	cd backend && $(BACKEND_PY) -m mypy $(BACKEND_FUTURE_TYPECHECK_TARGETS)

fmt: fmt-be fmt-fe

fmt-be:
	cd backend && $(BACKEND_PY) -m ruff format pli tests && $(BACKEND_PY) -m ruff check --fix pli tests

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
