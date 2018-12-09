"""This regression tests abstract rule which have an alternative with string
matches and a rule reference.

See https://github.com/igordejanovic/textX/pull/128

"""
from __future__ import unicode_literals
import sys
from textx import metamodel_from_str
from textx.scoping.tools import textx_isinstance

if sys.version < '3':
    text = unicode  # noqa
else:
    text = str

# Global variable namespace
namespace = {}


def test_abstract_alternative_string_match():

    grammar = r'''
    Calc: assignments*=Assignment expression=Expression;
    Assignment: variable=ID '=' expression=Expression ';';
    Expression: operands=Term (operators=PlusOrMinus operands=Term)*;
    PlusOrMinus: '+' | '-';
    Term: operands=Factor (operators=MulOrDiv operands=Factor)*;
    MulOrDiv: '*' | '/' ;
    Factor: (sign=PlusOrMinus)?  op=Operand;
    PrimitiveOperand: op_num=NUMBER | op_id=ID;
    Operand: PrimitiveOperand | ('(' Expression ')');
    '''

    calc_mm = metamodel_from_str(grammar)

    input_expr = '''
        a = 10;
        b = 2 * a + 17;
        -(4-1)*a+(2+4.67)+b*5.89/(.2+7)
    '''

    model = calc_mm.model_from_str(input_expr)

    def _is(x, rule):
        return textx_isinstance(x, calc_mm[rule])

    def assertIs(x, rule):
        assert _is(x, rule), 'Unexpected object "{}" to rule "{}"'\
                    .format(x, type(x), rule)

    def evaluate(x):

        if isinstance(x, float):
            return x

        elif _is(x, 'Expression'):
            ret = evaluate(x.operands[0])

            for operator, operand in zip(x.operators,
                                         x.operands[1:]):
                if operator == '+':
                    ret += evaluate(operand)
                else:
                    ret -= evaluate(operand)
            return ret

        elif _is(x, 'Term'):
            ret = evaluate(x.operands[0])

            for operator, operand in zip(x.operators,
                                         x.operands[1:]):
                if operator == '*':
                    ret *= evaluate(operand)
                else:
                    ret /= evaluate(operand)
            return ret

        elif _is(x, 'Factor'):
            value = evaluate(x.op)
            return -value if x.sign == '-' else value

        elif _is(x, 'Operand'):
            if _is(x, 'PrimitiveOperand'):
                if x.op_num is not None:
                    return x.op_num
                elif x.op_id:
                    if x.op_id in namespace:
                        return namespace[x.op_id]
                    else:
                        raise Exception('Unknown variable "{}" at position {}'
                                        .format(x.op_id, x._tx_position))
            else:
                assertIs(x, 'CompoundOperand')
                return evaluate(x.expression)

        elif _is(x, 'Calc'):
            for a in x.assignments:
                namespace[a.variable] = evaluate(a.expression)

            return evaluate(x.expression)

        else:
            assert False, 'Unexpected object "{}" of type "{}"'\
                    .format(x, type(x))

    result = evaluate(model)

    assert (result - 6.93805555) < 0.0001
