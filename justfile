# Define a variable with the python command to open a browser.
BROWSER := "uv run python -c 'import webbrowser, sys; webbrowser.open(sys.argv[1])'"

# show all available recipes
[default]
help:
    @just --list --unsorted --list-prefix '📜   '

# remove all build, test, coverage and Python artifacts
clean: clean-build clean-pyc clean-test

# remove build artifacts
[private]
clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

# remove Python file artifacts
[private]
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

# remove test and coverage artifacts
[private]
clean-test:
	rm -f .coverage
	rm -fr htmlcov/

# check style with ruff
lint flags="":
	uv run --no-default-groups --group test ruff check {{ flags }} textx/ tests/functional examples/

# run tests quickly with the default Python
test:
	uv run --no-default-groups --group test pytest tests/functional

# check code coverage quickly with the default Python
coverage:
	uv run --no-default-groups --group test coverage run --source textx -m pytest tests/functional
	uv run --no-default-groups --group test coverage report --fail-under 90
	uv run --no-default-groups --group test coverage html
	{{BROWSER}} htmlcov/index.html

# run static type checks
types:
	uv run --no-default-groups --group test mypy textx

# run all checks
check: check-format lint types coverage

[private]
check-ci: check-format lint types test

# format code with ruff
[no-cd]
format *paths=".":
    uv run ruff format {{ paths }}

[private]
check-format:
    uv run ruff format --check

# release package to PyPI test server
release-test: dist
	uv run flit publish --repository test

# release package to PyPI
release: dist
	uv run flit publish

# builds source and wheel package
dist: clean
	uv run flit build
	gpg --armor --detach-sign dist/*.whl
	gpg --armor --detach-sign dist/*.tar.gz
	ls -l dist

# install the package to the active Python's site-packages
install: clean
	uv pip install .

# setup development environment
dev: clean
	uv sync

# serve docs locally
docs:
	{{BROWSER}} "http://localhost:3000/"
	(cd docs && nix develop --command mdbook serve)
