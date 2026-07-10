.PHONY: install help venv api-dev api-build api-serve api-test api-test-coverage api-snapshot-update api-lint api-lint-fix api-typecheck api-docker-build api-helm-chart-upload web-dev web-build web-start web-test web-test-coverage web-snapshot-update web-lint web-lint-fix web-typecheck web-format web-format-check web-docker-build docker-up docker-down docker-logs docker-rebuild-api docker-logs-web docker-rebuild-web

.DEFAULT_GOAL := help

SHELL := $(CURDIR)/scripts/make-shell.sh

VENV := .venv
VENV_BIN := $(VENV)/bin
VENV_PYTHON := $(VENV_BIN)/python3
VENV_PIP := $(VENV_BIN)/pip

venv:
	@./scripts/ensure-venv.sh

# =============================================================================
# NX WORKSPACE COMMANDS
# =============================================================================

install: venv
	npm install
	$(VENV_PIP) install -e libs/py/common
	$(VENV_PIP) install -e "apps/api[dev]"

# =============================================================================
# API (BACKEND) COMMANDS
# =============================================================================

api-dev: venv
	npx nx dev api

api-build: venv
	npx nx build api

api-serve: venv
	npx nx serve api

api-test: venv
	npx nx test api

api-test-coverage: venv
	npx nx test:coverage api

api-snapshot-update: venv
	npx nx test:snapshot-update api

api-lint: venv
	npx nx lint api

api-lint-fix: venv
	npx nx lint:fix api

api-typecheck: venv
	npx nx typecheck api

api-docker-build: venv
	npx nx docker:build api

api-helm-chart-upload: venv
	npx nx helm-chart-upload api

# =============================================================================
# WEB (FRONTEND) COMMANDS
# =============================================================================

web-dev:
	npx nx dev web

web-build:
	npx nx build web

web-start:
	npx nx start web

web-test:
	npx nx test web

web-test-coverage:
	npx nx test:coverage web

web-snapshot-update:
	npx nx test:snapshot-update web

web-lint:
	npx nx lint web

web-lint-fix:
	npx nx lint:fix web

web-typecheck:
	npx nx typecheck web

web-format:
	npx nx format web

web-format-check:
	npx nx format:check web

web-docker-build:
	npx nx docker:build web

# =============================================================================
# DOCKER COMMANDS
# =============================================================================

docker-up:
	docker compose up -d --build api db web temporal

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f api

docker-rebuild-api:
	docker compose up -d --build api

docker-logs-web:
	docker compose logs -f web

docker-rebuild-web:
	docker compose up -d --build web

# =============================================================================
# APP COMMANDS — appended by api-bootstrap and web-bootstrap
# =============================================================================

help:
	@echo ""
	@echo "Run 'make <target>' to execute a command."
	@echo ""
	@echo "API:"
	@echo "  make api-dev              - Run backend in dev mode"
	@echo "  make api-build            - Build backend"
	@echo "  make api-serve            - Serve backend (no reload)"
	@echo "  make api-test             - Run backend tests"
	@echo "  make api-test-coverage    - Run backend tests with coverage"
	@echo "  make api-snapshot-update  - Update backend snapshots"
	@echo "  make api-lint             - Lint backend"
	@echo "  make api-lint-fix         - Fix backend linting"
	@echo "  make api-typecheck        - Type check backend"
	@echo "  make api-docker-build     - Build API Docker image"
	@echo "  make api-helm-chart-upload - Upload API Helm chart"
	@echo ""
	@echo "Web:"
	@echo "  make web-dev              - Run frontend in dev mode"
	@echo "  make web-build            - Build frontend"
	@echo "  make web-start            - Start frontend (production build)"
	@echo "  make web-test             - Run frontend tests"
	@echo "  make web-test-coverage    - Run frontend tests with coverage"
	@echo "  make web-lint             - Lint frontend"
	@echo "  make web-typecheck        - Type check frontend"
	@echo "  make web-docker-build     - Build web Docker image"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up            - Start API, database, web, and Temporal"
	@echo "  make docker-down          - Stop Docker Compose services"
	@echo "  make docker-logs          - Follow API container logs"
	@echo "  make docker-logs-web      - Follow web container logs"
	@echo "  make docker-rebuild-api   - Rebuild and restart API"
	@echo "  make docker-rebuild-web   - Rebuild and restart web"
