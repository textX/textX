
from __future__ import unicode_literals
import pytest

from textx.metamodel import metamodel_from_str
from textx.export import metamodel_export, model_export


def test_value_type():
    """
    Test object processors in context of match rules with base types.
    """

    grammar = """
        Program:
            'max_value' '=' max_value=INT
        ;
    """

    mm = metamodel_from_str(grammar)
    metamodel_export(mm, 'test_value_type.dot')

    model_str = """
            max_value = 5.5
    """

    # Test raises:
    # TextXSyntaxError: Expected 'EOF' at position (2, 26) => '_value = 5*.5.
    model = mm.model_from_str(model_str)
    model_export(model, 'test_value_type.dot')
