.PHONY: help clean clean-test clean-pyc clean-build lint test coverage types check release-test release dev test-env docs
.DEFAULT_GOAL := help
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts


clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:  ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:  ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr htmlcov/

lint:  ## check style with ruff
	uv run --no-default-groups --group test ruff check textx/ tests/functional examples/

test:  ## run tests quickly with the default Python
	uv run --no-default-groups --group test pytest tests/functional

coverage: ## check code coverage quickly with the default Python
	uv run --no-default-groups --group test coverage run --source textx -m pytest tests/functional
	uv run --no-default-groups --group test coverage report --fail-under 90
	uv run --no-default-groups --group test coverage html
	$(BROWSER) htmlcov/index.html

types:  ## Run static type checks
	uv run --no-default-groups --group test mypy textx

check: lint types coverage  ## Run all checks

release-test: dist ## release package to PyPI test server
	uv run flit publish --repository test

release: dist  ## release package to PyPI
	uv run flit publish

dist: clean ## builds source and wheel package
	uv run flit build
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	uv pip install .

dev: clean  ## Setup development environment
	uv sync --group test --group dev

docs:  ## Serve docs locally
	echo "Run 'docker stop textx-docs' from another terminal to gracefully terminate." 
	docker run -it --rm --name textx-docs -v .:/p -p 3000:3000 igordejanovic/mdbook-textx:latest mdbook serve docs -n 0.0.0.0
	$(BROWSER) "http://localhost:3000/"
