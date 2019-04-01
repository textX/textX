#!/bin/sh
# Run all tests and generate coverage report

coverage run --source textx -m py.test tests/functional
coverage report --fail-under 80
flake8
