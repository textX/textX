"""This regression tests abstract rule which have an alternative with string
matches and a rule reference.

See https://github.com/textX/textX/pull/128

"""
from textx import metamodel_from_str, textx_isinstance

# Global variable namespace
namespace = {}


def test_abstract_alternative_string_match():
    grammar = r"""
    Calc: assignments*=Assignment expression=Expression;
    Assignment: variable=ID '=' expression=Expression ';';
    Expression: operands=Term (operators=PlusOrMinus operands=Term)*;
    PlusOrMinus: '+' | '-';
    Term: operands=Factor (operators=MulOrDiv operands=Factor)*;
    MulOrDiv: '*' | '/' ;
    Factor: (sign=PlusOrMinus)?  op=Operand;
    PrimitiveOperand: op_num=NUMBER | op_id=ID;
    Operand: PrimitiveOperand | ('(' Expression ')');
    """

    calc_mm = metamodel_from_str(grammar)

    input_expr = """
        a = 10;
        b = 2 * a + 17;
        -(4-1)*a+(2+4.67)+b*5.89/(.2+7)
    """

    model = calc_mm.model_from_str(input_expr)

    def _is(x, rule):
        return textx_isinstance(x, calc_mm[rule])

    def assertIs(x, rule):
        assert _is(x, rule), f'Unexpected object "{x}" to rule "{rule}"'

    def evaluate(x):
        if isinstance(x, float):
            return x

        elif _is(x, "Expression"):
            ret = evaluate(x.operands[0])

            for operator, operand in zip(x.operators, x.operands[1:]):
                if operator == "+":
                    ret += evaluate(operand)
                else:
                    ret -= evaluate(operand)
            return ret

        elif _is(x, "Term"):
            ret = evaluate(x.operands[0])

            for operator, operand in zip(x.operators, x.operands[1:]):
                if operator == "*":
                    ret *= evaluate(operand)
                else:
                    ret /= evaluate(operand)
            return ret

        elif _is(x, "Factor"):
            value = evaluate(x.op)
            return -value if x.sign == "-" else value

        elif _is(x, "Operand"):
            if _is(x, "PrimitiveOperand"):
                if x.op_num is not None:
                    return x.op_num
                elif x.op_id:
                    if x.op_id in namespace:
                        return namespace[x.op_id]
                    else:
                        raise Exception(
                            f'Unknown variable "{x.op_id}" at position {x._tx_position}'
                        )
            else:
                assertIs(x, "CompoundOperand")
                return evaluate(x.expression)

        elif _is(x, "Calc"):
            for a in x.assignments:
                namespace[a.variable] = evaluate(a.expression)

            return evaluate(x.expression)

        else:
            raise AssertionError(f'Unexpected object "{x}" of type "{type(x)}"')

    result = evaluate(model)

    assert (result - 6.93805555) < 0.0001


def test_abstract_alternative_multiple_rules_raises_exception():
    """
    Test that multiple rules references in a single alternative of abstract
    rule is prohibited.
    """

    # In this grammar A is an abstract rule and referencing C D from second
    # alternative would yield just the first common rule object (C in this
    # case).
    grammar = r"""
    Model: a+=A;
    A: B | '(' C D ')';
    B: 'B' name=ID x=INT;
    C: 'C' name=ID;
    D: 'D' x=INT;
    """

    meta = metamodel_from_str(grammar)
    model = meta.model_from_str("B somename 23 ( C othername D 67 )")
    assert len(model.a) == 2
    assert model.a[0].name == "somename"
    assert model.a[0].x == 23
    assert type(model.a[1]).__name__ == "C"
    assert model.a[1].name == "othername"
