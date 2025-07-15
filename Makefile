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

# Docker
docker-build: ## Build l'image Docker
	docker build -t france-chomage-bot .

docker-run: ## Lance le container Docker
	docker run --env-file .env france-chomage-bot

docker-test: ## Test avec Docker
	docker run --env-file .env france-chomage-bot python -m france_chomage info

# Développement
dev-install: ## Installation pour développement
	pip install -r requirements.txt
	pip install black flake8 pytest-cov

dev-check: lint test ## Vérifications complètes de développement

# CI/CD
ci: install lint test ## Pipeline CI complète
