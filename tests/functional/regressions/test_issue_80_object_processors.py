from textx.metamodel import metamodel_from_str

call_counter = 0
grammar1 = """
foo:
    'foo' m_formula = Formula
;

Formula:
    ( values=FormulaExpression values='+' ( values=FormulaExpression)* )
;

FormulaExpression:
    values=bar
;

bar:
    m_id=/[a-f0-9]+/
;
"""

grammar2 = """
foo:
    'foo' m_formula = Formula
;

Formula:
    ( values=FormulaExpression ( values=FormulaExpression)* )
;

FormulaExpression:
    values=bar
;

bar:
    m_id=/[a-f0-9]+/
;
"""

grammar3 = """
foo:
    'foo' m_formula = Formula
;

Formula:
    ( values=FormulaExpression values='+' ( values=FormulaExpression)* )
;

FormulaExpression:
    values=/[a-f0-9]+/
;

"""


def default_processor(obj):
    global call_counter
    call_counter += 1
    print("PROCESSING " + str(obj.__class__.__name__))


def parse_str(grammar, lola_str):
    lola_str = lola_str
    obj_processors = {
        "foo": default_processor,
        "Formula": default_processor,
        "FormulaExpression": default_processor,
        "bar": default_processor,
    }

    meta_model = metamodel_from_str(grammar, ignore_case=True, auto_init_attributes=False)
    meta_model.register_obj_processors(obj_processors)
    model = meta_model.model_from_str(lola_str)
    return model


def test_issue_80_object_processors():
    global call_counter

    test_str = "foo a323 + a111"
    call_counter = 0
    parse_str(grammar1, test_str)
    assert call_counter == 6

    test_str = "foo a323 a111"
    call_counter = 0
    parse_str(grammar2, test_str)
    assert call_counter == 6

    test_str = "foo a323 + a111"
    call_counter = 0
    parse_str(grammar3, test_str)
    assert call_counter == 4
