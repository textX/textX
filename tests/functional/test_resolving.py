import pytest  # noqa
from textx import metamodel_from_str
from arpeggio import Sequence, OrderedChoice


def test_match_single_peg_rule_resolve():
    """
    Test that match rules with a single reference in rule
    body are properly resolved.
    """
    model = """
    Rule1: Rule2;
    Rule2: Rule3;
    Rule3: 'a' INT;
    """
    metamodel = metamodel_from_str(model)
    assert (
        metamodel["Rule1"]._tx_peg_rule
        == metamodel["Rule2"]._tx_peg_rule
        == metamodel["Rule3"]._tx_peg_rule
    )
    assert type(metamodel["Rule1"]._tx_peg_rule) is Sequence


def test_match_complex_recursive_peg_rule_resolve():
    """
    Test that recursive match rules are properly resolved.
    """
    grammar = """
        calc:       expression;
        factor:     INT | ('(' expression ')');
        term:       factor (term_op factor)*;
        term_op:    '*' | '/';
        expression: term  (expr_op term)*;
        expr_op:    '+' | '-';
    """
    metamodel = metamodel_from_str(grammar)

    assert metamodel._parser_blueprint.parser_model.nodes[0].rule_name == "expression"
    assert type(metamodel._parser_blueprint.parser_model.nodes[0]) is Sequence

    calc_rule = metamodel["calc"]._tx_peg_rule
    expression_rule = metamodel["expression"]._tx_peg_rule
    assert calc_rule is expression_rule
    assert type(calc_rule) is Sequence

    assert type(metamodel["term_op"]._tx_peg_rule) is OrderedChoice

    # Recursive factor rule
    factor_rule = metamodel["factor"]._tx_peg_rule
    # Find expression reference
    expr_ref = factor_rule.nodes[1].nodes[1]
    assert expr_ref.rule_name == "expression"
    assert type(expr_ref) is Sequence
    assert expr_ref is expression_rule
