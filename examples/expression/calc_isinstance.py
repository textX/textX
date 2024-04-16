
"""
This is a variant of calc example using textx_isinstance() to inspect object
types.
"""

from os.path import dirname, join

from textx import metamodel_from_str, textx_isinstance
from textx.export import metamodel_export, model_export

grammar = '''
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

# Global variable namespace
namespace = {}


def main(debug=False):

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
        assert _is(x, rule), f'Unexpected object "{x}" to rule "{rule}"'\
            

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
                        raise Exception(f'Unknown variable "{x.op_id}" '
                                        f'at position {x._tx_position}')
            else:
                assertIs(x, 'CompoundOperand')
                return evaluate(x.expression)

        elif _is(x, 'Calc'):
            for a in x.assignments:
                namespace[a.variable] = evaluate(a.expression)

            return evaluate(x.expression)

        else:
            raise AssertionError(f'Unexpected object "{x}" of type "{type(x)}"')
                

    result = evaluate(model)

    assert (result - 6.93805555) < 0.0001
    print("Result is", result)


if __name__ == '__main__':
    main()
