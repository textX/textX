#!/bin/sh
# Run all tests and generate coverage report

coverage run --source textx -m py.test tests/functional || exit 1
coverage report --omit textx/six.py --fail-under 80 || exit 1
flake8 || exit 1
