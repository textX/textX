from __future__ import unicode_literals
import pytest
from textx.metamodel import metamodel_from_str
from textx.exceptions import TextXSyntaxError


def test_noskipws():
    """
    Test 'noskipws' rule modifier.
    """
    grammar = """
    Rule:
        'entity' name=ID /\s*/ call=Rule2;
    Rule2[noskipws]:
        'first' 'second';
    """
    metamodel = metamodel_from_str(grammar)

    # Rule2 disables ws skipping so this will not parse.
    with pytest.raises(TextXSyntaxError):
        metamodel.model_from_str("entity Person first second")

    # This will parse.
    metamodel.model_from_str("entity Person firstsecond")


def test_skipws():
    """
    Test 'skipws' rule modifier.
    """
    grammar = """
    Rule:
        'entity' name=ID call=Rule2;
    Rule2[skipws]:
        'first' 'second';
    """

    # Change default behavior
    metamodel = metamodel_from_str(grammar, skipws=False)

    # Rule2 disables ws skipping but default rule is applied
    # for rule Rule so this will not parse.
    with pytest.raises(TextXSyntaxError):
        metamodel.model_from_str("entity Person first second")

    # This will parse.
    metamodel.model_from_str("entityPerson first  second")


def test_ws():
    """
    Test 'ws' rule modifier.
    """
    grammar = """
    Rule:
        'entity' name=ID /\s*/ call=Rule2;
    Rule2[ws='\n']:
        'first' 'second';
    """
    metamodel = metamodel_from_str(grammar)

    # Rule2 redefines ws to be newline only so
    # the space between 'first' and 'second' cannot
    # be skipped.
    with pytest.raises(TextXSyntaxError):
        metamodel.model_from_str("entity Person first second")

    # This will parse.
    metamodel.model_from_str("""entity Person first
second""")
