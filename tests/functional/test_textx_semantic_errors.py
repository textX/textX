from __future__ import unicode_literals
import pytest

from textx.metamodel import metamodel_from_str
from textx.exceptions import TextXSemanticError


def test_match_in_abstract():
    """
    Classes referenced from abstract rule can't be match rules.
    """

    grammar = """
    Rule1: Rule2 | Rule3 | Rule4;
    Rule2: a='a';
    Rule3: 'no' | 'match' | 'allowed';
    Rule4: b='b';
    """

    with pytest.raises(TextXSemanticError):
        metamodel_from_str(grammar)

