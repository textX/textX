# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from textx.metamodel import metamodel_from_str


def test_unicode_grammar_from_string():
    """
    Test grammar with unicode char given in grammar string.
    """

    grammar = """
    First:
        'first' a = Second
    ;

    Second:
        "Ω"|"±"|"♪"
    ;

    """

    metamodel = metamodel_from_str(grammar)
    assert metamodel


def test_unicode_grammar_from_file():
    """

    """
