#!/bin/sh

pip install --upgrade pip
pip install -e .
pip install -e tests/functional/subcommands/example_project
pip install -e tests/functional/registration/projects/types_dsl
pip install -e tests/functional/registration/projects/data_dsl
pip install -e tests/functional/registration/projects/flow_dsl
