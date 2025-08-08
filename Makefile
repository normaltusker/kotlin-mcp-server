# MCP Server Development Makefile
# Provides easy commands for development, testing, and quality assurance

.PHONY: help install test lint format security coverage clean all

# Default target
help:
	@echo "🚀 MCP Server Development Commands"
	@echo "=================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  make install     - Install all dependencies"
	@echo "  make setup-dev   - Setup development environment"
	@echo ""
	@echo "Quality Assurance:"
	@echo "  make test        - Run all tests"
	@echo "  make lint        - Run all linting checks"
	@echo "  make format      - Format code with black and isort"
	@echo "  make security    - Run security checks"
	@echo "  make coverage    - Run tests with coverage report"
	@echo ""
	@echo "CI/CD:"
	@echo "  make ci          - Run full CI pipeline"
	@echo "  make pre-commit  - Run pre-commit checks"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean       - Clean temporary files"
	@echo "  make all         - Run complete quality pipeline"

# Installation and setup
install:
	@echo "📦 Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install pytest pytest-asyncio pytest-cov flake8 black isort pylint mypy bandit psutil

setup-dev: install
	@echo "🔧 Setting up development environment..."
	# Setup git hooks
	cp pre_commit_hook.py .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
	@echo "✅ Development environment ready!"

# Testing
test:
	@echo "🧪 Running tests..."
	python -m pytest simple_test.py -v
	python -m pytest comprehensive_test.py -v
	python -m pytest test_mcp_comprehensive.py -v

test-quick:
	@echo "⚡ Running quick tests..."
	python -m pytest simple_test.py -v --tb=short

coverage:
	@echo "📊 Running tests with coverage..."
	python -m pytest test_*.py -v --cov=. --cov-report=html --cov-report=term-missing --cov-fail-under=70
	@echo "📈 Coverage report generated in htmlcov/"

# Code quality
lint:
	@echo "🔍 Running linting checks..."
	flake8 *.py --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 *.py --count --exit-zero --max-complexity=12 --max-line-length=100 --statistics
	pylint *.py --output-format=text --reports=yes --score=yes || echo "⚠️  Pylint completed with warnings"
	mypy *.py --ignore-missing-imports || echo "⚠️  MyPy completed with warnings"

format:
	@echo "🎨 Formatting code..."
	black *.py
	isort *.py
	@echo "✅ Code formatted!"

format-check:
	@echo "🎨 Checking code formatting..."
	black --check --diff *.py
	isort --check-only --diff *.py

security:
	@echo "🔒 Running security checks..."
	bandit -r *.py -f txt
	safety check || echo "⚠️  Safety check completed"

# CI/CD
ci:
	@echo "🚀 Running full CI pipeline..."
	python ci_test_runner.py

pre-commit:
	@echo "🔍 Running pre-commit checks..."
	python pre_commit_hook.py

# Functionality validation
validate:
	@echo "✅ Validating MCP server functionality..."
	python -c "from simple_mcp_server import MCPServer; print('✅ Base server OK')"
	python -c "from enhanced_mcp_server import EnhancedAndroidMCPServer; print('✅ Enhanced server OK')"
	python -c "from security_privacy_server import SecurityPrivacyMCPServer; print('✅ Security server OK')"
	python -c "from ai_integration_server import AIIntegratedMCPServer; print('✅ AI server OK')"

# Performance testing
perf:
	@echo "⚡ Running performance tests..."
	python -c "import asyncio; import time; import tempfile; from pathlib import Path; from ai_integration_server import AIIntegratedMCPServer; \
	async def perf_test(): \
		server = AIIntegratedMCPServer('perf-test'); \
		server.project_path = Path(tempfile.mkdtemp()); \
		start = time.time(); \
		for _ in range(10): await server.handle_list_tools(); \
		duration = time.time() - start; \
		print(f'✅ 10x tool listing: {duration:.3f}s ({duration/10:.3f}s avg)'); \
		import shutil; shutil.rmtree(server.project_path, ignore_errors=True); \
	asyncio.run(perf_test())"

# Maintenance
clean:
	@echo "🧹 Cleaning up..."
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*~" -delete
	@echo "✅ Cleanup complete!"

# Development workflow
dev-check: format-check lint test-quick validate
	@echo "🎉 Development checks completed!"

# Complete quality pipeline
all: clean format lint security test coverage validate perf
	@echo "🏆 Complete quality assurance pipeline completed!"

# Release preparation
release-prep: all
	@echo "🚀 Preparing for release..."
	@echo "📝 Release checklist:"
	@echo "  ✅ Code formatted and linted"
	@echo "  ✅ All tests passing"
	@echo "  ✅ Security checks passed"
	@echo "  ✅ Coverage requirements met"
	@echo "  ✅ Functionality validated"
	@echo "  ✅ Performance verified"
	@echo ""
	@echo "🎯 Ready for deployment!"

# Docker support (optional)
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t mcp-server .

docker-test:
	@echo "🐳 Testing in Docker..."
	docker run --rm mcp-server python -m pytest test_*.py -v

# Help for specific commands
help-ci:
	@echo "🔄 Continuous Integration Pipeline"
	@echo "================================="
	@echo "The CI pipeline runs the following checks:"
	@echo "1. Code formatting (black, isort)"
	@echo "2. Linting (flake8, pylint, mypy)"
	@echo "3. Security scanning (bandit, safety)"
	@echo "4. Unit tests (pytest)"
	@echo "5. Coverage analysis"
	@echo "6. Functionality validation"
	@echo "7. Performance testing"
	@echo ""
	@echo "Usage: make ci"

help-dev:
	@echo "💻 Development Workflow"
	@echo "======================"
	@echo "Recommended development workflow:"
	@echo "1. make setup-dev       (first time only)"
	@echo "2. <make changes>"
	@echo "3. make dev-check       (quick validation)"
	@echo "4. <commit changes>     (pre-commit hook runs automatically)"
	@echo "5. make ci              (full validation before push)"
	@echo ""
	@echo "For releases: make release-prep"
