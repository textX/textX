"""
Testing model and regexp with groups.
"""
import pytest  # noqa
from textx import metamodel_from_str

grammar = r"""
Model: entries += Entry;
Entry:
    'data' '=' data=/(?ms)\"{3}(.*?)\"{3}/
;
"""
grammar2 = r"""
Model:
    'data' '=' data=/(?ms)\"{3}(.*?)\"{3}\s*\-(\w+)\-/
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

    assert '"""' in m.entries[0].data  # """ is not removed
    assert "This" in m.entries[0].data  # This and text in model
    assert "text!" in m.entries[0].data  # This and text in model


def test_regexp_with_groups_activated():
    """
    Test that the grammar with w/o groups.
    """
    model_str = '''
    data = """
    This is a multiline
    text!
    """
    data="""second text"""
    '''

    metamodel = metamodel_from_str(grammar, use_regexp_group=True)
    m = metamodel.model_from_str(model_str)

    assert '"""' not in m.entries[0].data  # """ is not removed
    assert "This" in m.entries[0].data  # This and text in model
    assert "text!" in m.entries[0].data  # This and text in model


def test_regexp_with_groups_activated2():
    """
    Test that the grammar with with two groups in one regexp.
    This will not activate the group replacement
    """
    model_str = '''data = """This is a multiline"""-ExtraInfo-'''

    metamodel = metamodel_from_str(grammar2, use_regexp_group=True)
    m = metamodel.model_from_str(model_str)

    assert m.data == '"""This is a multiline"""-ExtraInfo-'
