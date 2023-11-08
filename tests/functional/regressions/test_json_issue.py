import pytest  # noqa
from textx.metamodel import metamodel_from_str
from textx.const import RULE_ABSTRACT, RULE_COMMON


def test_json_issue():
    """
    Test wrong rule type in json grammar.
    """
    grammar = """
    File:
        Array | Object
    ;

    Array:
        "[" values*=Value[','] "]"
    ;

    Value:
        STRING | FLOAT | BOOL | Object | Array | "null"
    ;

    Object:
        "{" members*=Member[','] "}"
    ;

    Member:
        key=STRING ':' value=Value
    ;
    """
    json_mm = metamodel_from_str(grammar)
    assert json_mm["Object"]._tx_type is RULE_COMMON
    assert json_mm["Member"]._tx_type is RULE_COMMON
    assert json_mm["Array"]._tx_type is RULE_COMMON
    assert json_mm["File"]._tx_type is RULE_ABSTRACT
    assert json_mm["Value"]._tx_type is RULE_ABSTRACT
