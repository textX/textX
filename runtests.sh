#!/bin/sh
# Run all tests and generate coverage report

pip install -e .
pip install -e tests/functional/subcommands/example_project
pip install -e tests/functional/registration/projects/types_dsl
pip install -e tests/functional/registration/projects/data_dsl
pip install -e tests/functional/registration/projects/flow_dsl

coverage run --source textx -m py.test tests/functional
coverage report --fail-under 80
flake8
