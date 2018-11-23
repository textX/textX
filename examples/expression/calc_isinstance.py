
"""
This is a variant of calc example using object processors for on-the-fly
evaluation.
"""

import sys
from os.path import join, dirname
from textx import metamodel_from_str
from textx.scoping.tools import textx_isinstance
from textx.export import metamodel_export, model_export

if sys.version < '3':
    text = unicode  # noqa
else:
    text = str

grammar = '''
Calc: assignments*=Assignment expression=Expression;
Assignment: variable=ID '=' expression=Expression ';';
Expression: operands=Term (operators=PlusOrMinus operands=Term)*;
PlusOrMinus: '+' | '-';
Term: operands=Factor (operators=MulOrDiv operands=Factor)*;
MulOrDiv: '*' | '/' ;
Factor: (sign=PlusOrMinus)?  op=Operand;
PrimitiveOperand: op_num=NUMBER | op_id=ID;
CompoundOperand: '(' expression=Expression ')';
Operand: PrimitiveOperand | CompoundOperand;
'''

# Global variable namespace
namespace = {}


def assignment_action(assignment):
    namespace[assignment.variable] = assignment.expression


def calc_action(calc):
    return calc.expression


def expression_action(expression):
    ret = expression.operands[0]
    for operator, operand in zip(expression.operators,
                                 expression.operands[1:]):
        if operator == '+':
            ret += operand
        else:
            ret -= operand
    return ret


def term_action(term):
    ret = term.operands[0]
    for operator, operand in zip(term.operators,
                                 term.operands[1:]):
        if operator == '*':
            ret *= operand
        else:
            ret /= operand
    return ret


def factor_action(factor):
    value = factor.op
    return -value if factor.sign == '-' else value


def operand_action(operand):
    if operand.op_num is not None:
        return operand.op_num
    elif operand.op_id:
        if operand.op_id in namespace:
            return namespace[operand.op_id]
        else:
            raise Exception('Unknown variable "{}" at position {}'
                            .format(operand.op_id, operand._tx_position))
    else:
        return operand.op_expr


def main(debug=False):

    processors = {
        'Calc': calc_action,
        'Assignment': assignment_action,
        'Expression': expression_action,
        'Term': term_action,
        'Factor': factor_action,
        'Operand': operand_action
    }

    calc_mm = metamodel_from_str(grammar, auto_init_attributes=False,
                                 debug=debug)
    this_folder = dirname(__file__)
    if debug:
        metamodel_export(calc_mm, join(this_folder, 'calc_metamodel.dot'))

    input_expr = '''
        a = 10;
        b = 2 * a + 17;
        -(4-1)*a+(2+4.67)+b*5.89/(.2+7)
    '''

    model = calc_mm.model_from_str(input_expr)

    if debug:
        model_export(model, join(this_folder, 'calc_model.dot'))

    # test whether x is an instance of a certain rule
    # note that it is different than comparing to x.__class__.__name__
    # because the latter only tests for the most derived type and
    # wont be helpful for abstract rules
    def _is(x, rule):
        return textx_isinstance(x, calc_mm[rule])

    def assertIs(x, rule):
        assert _is(x, rule), 'Unexpected object "{}" of type "{}" to rule "{}"'\
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
    print("Result is", result)


if __name__ == '__main__':
    main()
