from textx import metamodel_from_str

grammar = """
Model:
    types+=Type
    entities+=Entity
;

Type:
    'type' name=ID
;

Entity:
    'entity' name=ID '{'
        properties+=Property
    '}'
;

Property:
    type=[Type] name=ID
;
"""

modelstr = """
type STR
type INT

entity Point {
    INT x
    INT y
}

entity Person {
    STR name
    INT age
}
"""


def test_textx_tools_support():
    # textx_tools_support disabled (default)
    mm = metamodel_from_str(grammar)
    model = mm.model_from_str(modelstr)
    assert not hasattr(model, "_pos_crossref_list")
    assert not hasattr(model, "_pos_rule_dict")

    # textx_tools_support enabled
    mm = metamodel_from_str(grammar, textx_tools_support=True)
    model = mm.model_from_str(modelstr)
    # check additional properties
    assert hasattr(model, "_pos_crossref_list")
    assert hasattr(model, "_pos_rule_dict")
    # check number of crossrefs
    assert len(model._pos_crossref_list) == 4
    # check rule dictionary key order
    rules_keys = list(model._pos_rule_dict)
    rules_len = len(rules_keys)
    assert rules_len > 0
    assert rules_keys[0][0] > rules_keys[rules_len - 1][0]
