# ╔═══════════════════════════════════════════════════════════════════╗
# ║  JOBPILOT — Makefile                                             ║
# ║  Common commands for development                                  ║
# ╚═══════════════════════════════════════════════════════════════════╝

.PHONY: help setup db backend frontend dev clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## First-time setup: install all dependencies
	@echo "📦 Setting up backend..."
	cd backend && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	@echo "🎭 Installing Playwright browsers..."
	cd backend && . venv/bin/activate && playwright install chromium
	@echo "📦 Setting up frontend..."
	cd frontend && npm install
	@echo "📄 Copying env template..."
	cp -n .env.example .env 2>/dev/null || true
	@echo "✅ Setup complete! Edit .env with your API keys, then run 'make dev'"

db: ## Start MongoDB via Docker
	docker-compose up -d mongodb
	@echo "✅ MongoDB running on localhost:27017"

backend: ## Start the backend server
	cd backend && . venv/bin/activate && uvicorn main:app --reload --port 8000

frontend: ## Start the frontend dev server
	cd frontend && npm run dev

dev: db ## Start everything (MongoDB + backend + frontend)
	@echo "🚀 Starting JobPilot..."
	$(MAKE) -j2 backend frontend

clean: ## Stop all containers and remove volumes
	docker-compose down -v
	@echo "🧹 Cleaned up"

lint: ## Run linting on backend
	cd backend && . venv/bin/activate && ruff check .

test: ## Run backend tests
	cd backend && . venv/bin/activate && pytest -v
