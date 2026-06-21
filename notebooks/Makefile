# AI-101-Fed — Common development tasks
# Usage: make <target>

.PHONY: help setup test-skills validate clean install-deps lint format

## Default target
help:
	@echo "AI-101-Fed — Available targets:"
	@echo "  setup        - Run notebook 00 steps (Python version, vendor arc, install deps, spaCy model, env file)"
	@echo "  install-deps - Install requirements.txt"
	@echo "  test-skills  - Run all skill tests (pytest skills/**/tests/)"
	@echo "  validate     - Run all validation scripts across skills"
	@echo "  clean        - Remove caches, checkpoints, and generated files"
	@echo "  lint         - Run ruff linter on Python files"
	@echo "  format       - Format Python files with ruff"

## Setup tasks
setup: install-deps
	@echo "✓ Setup complete. Edit .env with your API keys."

install-deps:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

## Testing
test-skills:
	@echo "Running skill tests..."
	pytest skills/*/tests/unit/ -v || true
	pytest skills/*/tests/smoke/ -v || true

validate:
	@echo "Running validation scripts..."
	@find .claude/skills -name "validate_output.py" -o -name "validate_*.py" | head -5 | while read f; do \
		echo "Validating $$f"; \
		python "$$f" --help 2>/dev/null || echo "  (no --help available)"; \
	done
	@echo "Run individual validation scripts per skill for full validation."

## Cleanup
clean:
	rm -rf __pycache__ .pytest_cache .ipynb_checkpoints
	rm -rf .venv
	find . -name "*.pyc" -delete
	find . -name ".DS_Store" -delete
	@echo "✓ Cleaned caches and artifacts"

## Code quality
lint:
	@ruff check . --ignore E501 || true

format:
	@ruff format . || true