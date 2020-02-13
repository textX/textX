#!/bin/sh

pip install --upgrade pip || exit 1
pip install -e .[dev] || exit 1
./install-test.sh
