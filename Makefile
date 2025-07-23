# 🇫🇷 France Chômage Bot - Makefile

.PHONY: help install test test-cov lint format clean run-scheduler run-scrape docker-build docker-run

help: ## Affiche cette aide
	@echo "🇫🇷 France Chômage Bot - Commandes disponibles:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Installe les dépendances
	pip install -r requirements.txt

test: ## Lance les tests
	pytest

test-cov: ## Lance les tests avec couverture
	pytest --cov=france_chomage --cov-report=html --cov-report=term

lint: ## Vérifie le code avec flake8
	flake8 france_chomage/ --max-line-length=100 --ignore=E203,W503

format: ## Formate le code avec black
	black france_chomage/ --line-length=100

clean: ## Nettoie les fichiers temporaires
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -f jobs*.json jobs*.csv

# Commandes d'utilisation
run-scheduler: ## Lance le scheduler principal
	python -m france_chomage scheduler

run-scrape-comm: ## Scrape les offres de communication
	python -m france_chomage scrape communication

run-scrape-design: ## Scrape les offres de design
	python -m france_chomage scrape design

run-workflow-comm: ## Workflow complet communication
	python -m france_chomage workflow communication

run-workflow-design: ## Workflow complet design
	python -m france_chomage workflow design

test-config: ## Test la configuration
	python -m france_chomage test

info: ## Affiche les informations de configuration
	python -m france_chomage info

validate-config: ## Valide la configuration des topics
	@echo "🔍 Validation de la configuration des topics:"
	@python -c "from france_chomage.config import settings; print(f'✅ Communication topic: {settings.communication_topic_id}'); print(f'✅ Design topic: {settings.design_topic_id}'); print('✅ Configuration valide - topics séparés OK')"

# Database commands
db-init: ## Initialize database tables (safe, preserves existing data)
	python -m france_chomage db init

db-migrate: ## Migrate JSON files to database
	python -m france_chomage db migrate

db-status: ## Show database status
	python -m france_chomage db status

db-cleanup: ## Clean up old jobs (90+ days)
	python -m france_chomage db cleanup

db-backup: ## Backup database to JSON files
	python -m france_chomage db backup

# Migration management
migrate-check: ## Check migration status
	python -m france_chomage migrate check

migrate-upgrade: ## Apply pending migrations
	python -m france_chomage migrate upgrade

migrate-create: ## Create new migration (requires message)
	@read -p "Migration message: " msg; python -m france_chomage migrate revision -m "$$msg"

migrate-history: ## Show migration history
	python -m france_chomage migrate history

# Railway deployment
railway-deploy: ## Deploy to Railway (requires Railway CLI)
	railway up

railway-logs: ## Show Railway logs
	railway logs

railway-status: ## Show Railway deployment status
	railway status

railway-vars: ## Show Railway environment variables
	railway variables

# Docker
docker-build: ## Build l'image Docker
	docker build -t france-chomage-bot .

docker-run: ## Lance le container Docker (standalone)
	docker run --env-file .env france-chomage-bot

docker-test: ## Test avec Docker (standalone)
	docker run --env-file .env france-chomage-bot python -m france_chomage info

# Docker Compose (recommended for production)
docker-up: ## Start services with database
	cd deployment/docker && docker-compose up -d

docker-down: ## Stop all services
	cd deployment/docker && docker-compose down

docker-logs: ## Show application logs
	cd deployment/docker && docker-compose logs -f app

docker-db-logs: ## Show database logs
	cd deployment/docker && docker-compose logs -f db

docker-admin: ## Start with database admin interface
	cd deployment/docker && docker-compose --profile admin up -d

docker-rebuild: ## Rebuild and restart
	cd deployment/docker && docker-compose down
	cd deployment/docker && docker-compose build --no-cache
	cd deployment/docker && docker-compose up -d

docker-clean: ## Clean up containers and volumes
	cd deployment/docker && docker-compose down -v
	docker system prune -f

# Développement
dev-install: ## Installation pour développement
	pip install -r requirements.txt
	pip install black flake8 pytest-cov

dev-check: lint test ## Vérifications complètes de développement

# CI/CD
ci: install lint test ## Pipeline CI complète
