# IndiaLens Developer Commands

.PHONY: help dev-frontend dev-backend dev db-up db-down db-shell db-migrate \
        scrape-test test lint format clean \
        ml-train ml-status ml-retrain ml-ner-data

# ── Help ──────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  IndiaLens Development Commands"
	@echo "  ═══════════════════════════════════════════════════════"
	@echo "  make dev            Start full stack (frontend + backend)"
	@echo "  make dev-frontend   Start Next.js dev server only (port 3000)"
	@echo "  make dev-backend    Start FastAPI only (port 8000)"
	@echo "  make db-up          Start Postgres + Redis via Docker"
	@echo "  make db-down        Stop Docker services"
	@echo "  make db-shell       psql into indialens DB"
	@echo "  make db-migrate     Apply schema.sql to local DB"
	@echo "  make airflow-up     Start full Airflow stack"
	@echo "  make scrape-test    Run NIRF scraper in dry-run mode"
	@echo "  make test           Run backend test suite"
	@echo "  make lint           Lint Python (ruff) + TypeScript (eslint)"
	@echo "  make format         Auto-format Python (black) + TS (prettier)"
	@echo "  make clean          Remove __pycache__, .pyc files"
	@echo ""

# ── Full dev stack ─────────────────────────────────────────────────
dev: db-up
	@echo "Starting frontend and backend in parallel..."
	(cd indialens && npm run dev) & \
	(cd backend && uvicorn api.main:app --reload --port 8000) & \
	wait

# ── Frontend only ─────────────────────────────────────────────────
dev-frontend:
	cd indialens && npm run dev

# ── Backend only ──────────────────────────────────────────────────
dev-backend: db-up
	cd backend && uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# ── Database ──────────────────────────────────────────────────────
db-up:
	cd backend && docker compose up -d postgres redis
	@echo "Waiting for Postgres to be ready..."
	@sleep 3
	@echo "✓ Postgres running on localhost:5432"
	@echo "✓ Redis running on localhost:6379"

db-down:
	cd backend && docker compose down

db-shell:
	docker exec -it $$(docker ps -q -f name=postgres) psql -U indialens -d indialens

db-migrate:
	docker exec -i $$(docker ps -q -f name=postgres) psql -U indialens -d indialens \
		< backend/db/schema.sql
	@echo "✓ Schema applied"

db-seed:
	@echo "Seeding DB with 15 mock records..."
	cd backend && python -m scripts.seed_db
	@echo "✓ Seed complete"

# ── Airflow ───────────────────────────────────────────────────────
airflow-up:
	cd backend && docker compose up -d
	@echo "✓ Airflow webserver: http://localhost:8080 (admin/admin123)"
	@echo "✓ FastAPI docs:      http://localhost:8000/api/docs"

airflow-down:
	cd backend && docker compose down

airflow-trigger:
	@echo "Triggering weekly scrape DAG..."
	docker exec $$(docker ps -q -f name=airflow-scheduler) \
		airflow dags trigger indialens_weekly_scrape

# ── Scraper tests ─────────────────────────────────────────────────
scrape-test:
	cd backend && python -m scrapers.nirf_scraper --dry-run

scrape-reddit:
	cd backend && python -m scrapers.reddit_scraper --dry-run --limit 10

scrape-worldbank:
	cd backend && python -m scrapers.worldbank_scraper --dry-run

scrape-plfs:
	cd backend && python -m scrapers.plfs_scraper --dry-run

scrape-internshala:
	cd backend && python -m scrapers.internshala_scraper --dry-run

scrape-indeed:
	cd backend && python -m scrapers.indeed_scraper --dry-run

scrape-placement:
	cd backend && python -m scrapers.college_placement_scraper --dry-run

# ── Testing ───────────────────────────────────────────────────────
test:
	cd backend && python -m pytest tests/ -v --tb=short

test-watch:
	cd backend && python -m pytest tests/ -v -f

# ── Code quality ──────────────────────────────────────────────────
lint:
	cd backend && ruff check .
	cd indialens && npx eslint src/ --ext .ts,.tsx

format:
	cd backend && black . && ruff check . --fix
	cd indialens && npx prettier --write src/

# ── Utilities ─────────────────────────────────────────────────────
clean:
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find backend -name "*.pyc" -delete 2>/dev/null || true
	find backend -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleaned"

install:
	cd indialens && npm install
	cd backend && pip install -r requirements.txt

# ── Frontend build ────────────────────────────────────────────────
build-frontend:
	cd indialens && npm run build

type-check:
	cd indialens && npx tsc --noEmit

# ── Week 3: ML targets ─────────────────────────────────────────────
ml-train:
	@echo "Training XGBoost + LSTM from seed data..."
	cd backend && python -m ml.training_pipeline
	@echo "✓ Models saved to backend/ml/artifacts/"

ml-status:
	@echo "Fetching model status from FastAPI..."
	curl -s http://localhost:8000/api/ml/status | python3 -m json.tool

ml-retrain:
	@echo "Triggering async retrain via admin API..."
	@if [ -z "$(ADMIN_KEY)" ]; then \
		echo "Set ADMIN_KEY=<your key> before running this target"; exit 1; \
	fi
	curl -s -X POST http://localhost:8000/api/ml/retrain \
		-H "X-API-KEY: $(ADMIN_KEY)" | python3 -m json.tool

ml-ner-data:
	@echo "Generating synthetic NER training data..."
	cd backend && python -c "from ml.salary_ner import generate_training_data; generate_training_data()"
	@echo "✓ Training data → backend/ml/artifacts/ner_training.jsonl"

ml-feature-importance:
	@echo "XGBoost top features (y5 model):"
	curl -s http://localhost:8000/api/ml/feature-importance | python3 -m json.tool

# ── Production deployment ──────────────────────────────────────────
deploy-backend:
	cd backend && railway up

deploy-frontend:
	cd indialens && vercel --prod

deploy-all: deploy-backend deploy-frontend

# ── GitHub Actions simulation (local test) ────────────────────────
run-all-scrapers-dry:
	cd backend && for scraper in worldbank plfs nirf payscale naukri internshala indeed reddit college_placement; do \
		echo "\n>>> Running $$scraper..."; \
		python -m scrapers.$${scraper}_scraper --dry-run 2>&1 | tail -5; \
	done

health-check:
	curl -s http://localhost:8000/health | python3 -m json.tool
