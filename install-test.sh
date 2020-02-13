#!/bin/sh

pip install --upgrade pip || exit 1
pip install -e .[test] || exit 1
pip install -e tests/functional/subcommands/example_project || exit 1
pip install -e tests/functional/registration/projects/types_dsl || exit 1
pip install -e tests/functional/registration/projects/data_dsl || exit 1
pip install -e tests/functional/registration/projects/flow_dsl || exit 1
pip install -e tests/functional/registration/projects/flow_codegen || exit 1
