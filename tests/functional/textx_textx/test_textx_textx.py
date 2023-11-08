from os.path import abspath, dirname, join

from textx import get_children_of_type, metamodel_for_language


def test_textx_textx():
    """
    Test textX definition in textX. Used to analyze grammars programmatically.
    """

    textx_mm = metamodel_for_language("textx")
    grammar_model = textx_mm.grammar_model_from_file(
        join(abspath(dirname(__file__)), "pyflies.tx")
    )

    def get_rule_by_name(name):
        return next(x for x in grammar_model.rules if x.name == name)

    # Check rules with params
    rule_with_params = get_rule_by_name("TestType")
    assert len(rule_with_params.params) == 2
    p = rule_with_params.params
    assert p[0].name == "noskipws"
    assert p[1].name == "my_param"
    assert p[1].value == "some value"

    # Check string matches in the rule
    str_matches = get_children_of_type("StrMatch", rule_with_params)
    assert len(str_matches) == 3
    assert str_matches[1].match == "{"

    # Check match ordered choice
    rule = get_rule_by_name("FixedConditionEnum")
    assert len(rule.body.sequences) == 4
    assert rule.body.sequences[0].repeatable_exprs[0].expr.simple_match.match == "all"

    # Referencing languages
    assert len(grammar_model.imports_or_references) == 3
    ref = grammar_model.imports_or_references[2]
    assert ref.language_name == "some-other-language"
    assert ref.language_alias == "o"
