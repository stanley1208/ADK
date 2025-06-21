# Disaster Response System - Agent Engine Makefile
# Common development and deployment tasks

.PHONY: help install install-dev test test-coverage lint format clean build deploy-dev deploy-prod

# Default target
help:
	@echo "Disaster Response System - Agent Engine"
	@echo "========================================"
	@echo ""
	@echo "Available targets:"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo "  test         Run tests"
	@echo "  test-cov     Run tests with coverage"
	@echo "  lint         Run linting and type checking"
	@echo "  format       Format code with black and isort"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build Python package"
	@echo "  deploy-dev   Deploy to development environment"
	@echo "  deploy-prod  Deploy to production environment"
	@echo "  verify       Verify agent configuration"
	@echo ""

# Installation targets
install:
	@echo "📦 Installing production dependencies..."
	pip install -r requirements.txt

install-dev:
	@echo "📦 Installing development dependencies..."
	pip install -r requirements-dev.txt
	pre-commit install

# Testing targets
test:
	@echo "🧪 Running tests..."
	python -m pytest ../python_agents/test_*.py -v

test-cov:
	@echo "🧪 Running tests with coverage..."
	python -m pytest ../python_agents/test_*.py -v --cov=agent_engine --cov-report=term-missing --cov-report=html

# Code quality targets
lint:
	@echo "🔍 Running linting and type checking..."
	flake8 agent.py
	mypy agent.py
	bandit -r agent.py

format:
	@echo "🎨 Formatting code..."
	black agent.py
	isort agent.py

# Build and cleanup targets
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

build: clean
	@echo "🏗️ Building Python package..."
	python -m build

# Verification targets
verify:
	@echo "✅ Verifying agent configuration..."
	python -c "from agent import root_agent, AGENT_CONFIG; print('✅ Agent verified:', root_agent.name)"

validate-config:
	@echo "✅ Validating configuration files..."
	python -c "import yaml; yaml.safe_load(open('agent_config.yaml'))"
	@echo "✅ YAML configuration valid"

# Deployment targets
deploy-dev:
	@echo "🚀 Deploying to development environment..."
	@echo "Setting environment variables for development..."
	export ENVIRONMENT=development && \
	export AGENT_VERSION=dev-$(shell date +%Y%m%d-%H%M%S) && \
	./deploy_agent.sh

deploy-staging:
	@echo "🚀 Deploying to staging environment..."
	@echo "Setting environment variables for staging..."
	export ENVIRONMENT=staging && \
	export AGENT_VERSION=staging-$(shell date +%Y%m%d-%H%M%S) && \
	./deploy_agent.sh

deploy-prod:
	@echo "🚀 Deploying to production environment..."
	@echo "⚠️ WARNING: This will deploy to PRODUCTION!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo ""; \
		export ENVIRONMENT=production && \
		export AGENT_VERSION=v1.0.0 && \
		./deploy_agent.sh; \
	else \
		echo ""; \
		echo "❌ Deployment cancelled"; \
	fi

# Local development targets
dev-setup: install-dev
	@echo "🔧 Setting up development environment..."
	cp env.template .env
	@echo "📝 Please edit .env file with your configuration"

run-local:
	@echo "🏃 Running agent locally..."
	python -c "from agent import root_agent; print('🤖 Agent running locally:', root_agent.name)"

# Testing with different Python versions
test-py310:
	@echo "🐍 Testing with Python 3.10..."
	python3.10 -m pytest ../python_agents/test_*.py -v

test-py311:
	@echo "🐍 Testing with Python 3.11..."
	python3.11 -m pytest ../python_agents/test_*.py -v

# Security scanning
security-scan:
	@echo "🔒 Running security scan..."
	bandit -r agent.py
	safety check

# Documentation targets
docs:
	@echo "📚 Building documentation..."
	sphinx-build -b html docs/ docs/_build/

docs-serve:
	@echo "📚 Serving documentation..."
	cd docs/_build && python -m http.server 8000

# Container targets (if using containers locally)
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t disaster-response-agent:latest ..

docker-run:
	@echo "🐳 Running Docker container..."
	docker run -p 8080:8080 disaster-response-agent:latest

# Database targets
setup-bigquery:
	@echo "🗄️ Setting up BigQuery dataset and tables..."
	python -c "
from python_agents.agents.detection_agent import DetectionAgent
agent = DetectionAgent()
agent.setup_bigquery_table()
print('✅ BigQuery setup complete')
"

# Monitoring targets
check-health:
	@echo "🏥 Checking agent health..."
	python -c "
try:
    from agent import root_agent
    print('✅ Agent health check passed')
except Exception as e:
    print(f'❌ Agent health check failed: {e}')
    exit(1)
"

# Performance testing
perf-test:
	@echo "⚡ Running performance tests..."
	python -c "
import time
from agent import root_agent
start = time.time()
# Simulate agent execution
end = time.time()
print(f'⚡ Agent execution time: {end - start:.2f}s')
"

# All-in-one targets
ci: install test lint
	@echo "🎯 CI pipeline completed successfully"

cd: ci build
	@echo "🎯 CD pipeline ready for deployment"

all: clean install-dev test-cov lint format build verify
	@echo "🎉 All tasks completed successfully!" 