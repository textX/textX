#!/bin/sh
# Run all tests and generate coverage report

coverage run --source textx -m py.test tests/functional || exit 1
coverage report --omit textx/six.py --fail-under 80 || exit 1
# Run this to generate html report
# coverage html --omit textx/six.py --directory=coverage
flake8 || exit 1
