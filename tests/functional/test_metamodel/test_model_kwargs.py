from __future__ import unicode_literals
import pytest  # noqa
import os
import os.path
from pytest import raises
from textx import (metamodel_from_str,
                   metamodel_for_language,
                   register_language, clear_language_registrations)
import textx.scoping.providers as scoping_providers
import textx.scoping as scoping
import textx.scoping.tools as tools
import textx.exceptions


grammar = r"""
Model: 'MyModel' name=ID;
"""

text = r"""
MyModel test1
"""

def test_model_kwargs():
    mm = metamodel_from_str(grammar)
    m = mm.model_from_str(text, parameter1='P1', parameter2='P2')
    assert m.name == 'test1'
    assert hasattr(m, '_tx_model_kwargs')
    assert len(m._tx_model_kwargs) == 2
    assert m._tx_model_kwargs['parameter1'] == 'P1'
    assert m._tx_model_kwargs['parameter2'] == 'P2'
