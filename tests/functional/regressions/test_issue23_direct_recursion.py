import pytest  # noqa

from textx.metamodel import metamodel_from_str
from textx.const import RULE_COMMON, RULE_ABSTRACT, RULE_MATCH


def test_issue_23():
    """
    Test that rule types are correctly determined on direct recursion.
    """

    grammar = """
    List: members+=Value;
    Value: ('{' List '}') | ID;
    """
    mm = metamodel_from_str(grammar)

    assert mm["List"]._tx_type is RULE_COMMON
    assert mm["Value"]._tx_type is RULE_ABSTRACT
    assert mm["Value"]._tx_inh_by == [mm["List"]]

    grammar = """
    List: '{' members+=Value '}';
    Value: ID;
    """
    mm = metamodel_from_str(grammar)

    assert mm["List"]._tx_type is RULE_COMMON
    assert mm["Value"]._tx_type is RULE_MATCH

    grammar = """
    ListSyntax: '{' List '}';
    List: members+=Value;
    Value: ListSyntax | ID;
    """
    mm = metamodel_from_str(grammar)

    assert mm["ListSyntax"]._tx_type is RULE_ABSTRACT
    assert mm["ListSyntax"]._tx_inh_by == [mm["List"]]
    assert mm["List"]._tx_type is RULE_COMMON
    assert mm["Value"]._tx_type is RULE_ABSTRACT
    assert mm["Value"]._tx_inh_by == [mm["ListSyntax"]]
