from textx import metamodel_from_str


def test_noskipws_modifier_with_int_rule():
    """
    Tests that noskipsws rule modifier works with INT rule.
    """
    grammar = r"""
    AssessmentEnd:
        'completion_time' ':' /\s*/ completion_time=TimeHours
    ;

    TimeHours[noskipws]:
        hours=INT 'h'
    ;
    """

    meta = metamodel_from_str(grammar)
    s = """completion_time: 1h"""

    model = meta.model_from_str(s)
    assert model is not None
