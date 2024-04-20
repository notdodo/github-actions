.PHONY: format
format: ## Format repository code
	poetry run black .
	poetry run isort .

.PHONY: lint
lint: ## Launch the linting tools
	poetry run flake8 .
	poetry run pylint *.py

.PHONY: type-check
type-check: ## Launch the type checking tool
	poetry run mypy .

.PHONY: check
check: format-check lint type-check ## Launch all the checks in RO (formatting, linting, type checking)

.PHONY: all
all: format lint type-check ## Launch all the checks and formatting

.PHONY: help
help: ## Show the available commands
	@echo Available commands:
ifeq ($(OS),Windows_NT)
	@for /f "tokens=1,2* delims=#" %%a in ('@findstr /r /c:"^[a-zA-Z-_]*:[ ]*## .*$$" $(MAKEFILE_LIST)') do @echo %%a%%b
else
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
endif