from textx import metamodel_from_str

grammar = """
Calc: expression=Expression;
Expression: op=Term (op=PlusOrMinus op=Term)* ;
PlusOrMinus: '+' | '-';
Term: op=Factor (op=MulOrDiv op=Factor)*;
MulOrDiv: '*' | '/' ;
Factor: (sign=PlusOrMinus)?  op=Operand;
Operand: op=NUMBER | op=ID | ('(' op=Expression ')');
"""


class Calc:
    def __init__(self, expression):
        # A simple reduction to trigger the #310 problem
        # Here, we reduce the expression as it is only a multiplication
        # e.g. no +/- operation so no need for Expression intermediate node
        if len(self.expression.op) == 1:
            self.expression = self.expression.op[0]


def test_non_abstract_grammar_rule_different_from_obj_metaclass():
    """
    Test that if model is modified (e.g. reduced) from user classes the actual
    type of the attribute might be different from grammar declared although the
    grammar rule is not abstract.

    """
    mm = metamodel_from_str(grammar, classes=[Calc])
    model = mm.model_from_str("2 * 5")
    assert model.expression.__class__.__name__ == "Term"
