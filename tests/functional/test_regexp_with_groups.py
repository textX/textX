"""
Testing model and regexp with groups.
"""
from __future__ import unicode_literals
import pytest  # noqa
import sys
from textx import metamodel_from_str

if sys.version < '3':
    text = unicode  # noqa
else:
    text = str

grammar = """
Model:
    'data' '=' data=/\"(?ms){3}(.*)?\"{3}/
;
"""
grammar2 = """
Model:
    'data' '=' data=/\"(?ms){3}(.*)?\"{3}\s*\-(\w+)\-/
;
"""

def test_regexp_with_groups_deactivated():
    """
    Test that the grammar with w/o groups.
    """
    model_str = '''
    data = """
    This is a multiline
    text!
    """
    '''

    metamodel = metamodel_from_str(grammar)
    m = metamodel.model_from_str(model_str)

    assert '"""' in m.data  # """ is not removed
    assert 'This' in m.data  # This and text in model
    assert 'text!' in m.data  # This and text in model

def test_regexp_with_groups_activated():
    """
    Test that the grammar with w/o groups.
    """
    model_str = '''
    data = """
    This is a multiline
    text!
    """
    '''

    metamodel = metamodel_from_str(grammar)
    m = metamodel.model_from_str(model_str)

    assert '"""' not in m.data  # """ is not removed
    assert 'This' in m.data  # This and text in model
    assert 'text!' in m.data  # This and text in model

def test_regexp_with_groups_activated2():
    """
    Test that the grammar with w/o groups.
    """
    model_str = '''
    data = """This is a multiline"""-ExtraInfo-
    '''

    metamodel = metamodel_from_str(grammar2)
    m = metamodel.model_from_str(model_str)

    assert 'This is a multilineExtraInfo' == m.data
