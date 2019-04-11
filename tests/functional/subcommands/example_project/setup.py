#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='textX-subcommand-test',
    packages=["textx_subcommand_test"],
    entry_points={
        'textx_commands': [
            'testcommand = textx_subcommand_test.cli:testcommand',
            'testgroup = textx_subcommand_test.cli:create_testgroup'
        ]
    }
)
