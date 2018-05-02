"""
This is a variant of calc example using object processors for on-the-fly
evaluation.
"""
import sys
from textx import metamodel_from_str

if sys.version < '3':
    text = unicode  # noqa
else:
    text = str

grammar = '''
Calc: assignments*=Assignment expression=Expression;
Assignment: variable=ID '=' expression=Expression ';';
Expression: left=Term (op=PlusOrMinus right=Expression)?;
PlusOrMinus: '+' | '-';
Term: left=Factor (op=MulOrDiv right=Expression)?;
MulOrDiv: '*' | '/' ;
Factor: (sign=PlusOrMinus)?  op=Operand;
Operand: op=NUMBER | op=ID | ('(' op=Expression ')');
'''

# Global variable namespace
namespace = {}


def assignment_action(assignment):
    import pudb;pudb.set_trace()
    namespace[assignment.variable] = assignment.expression


def calc_action(calc):
    return calc.expression


def expression_action(expression):
    import pudb;pudb.set_trace()
    if expression.op == '+':
        return expression.left + expression.right
    elif expression.op == '-':
        return expression.left - expression.right
    else:
        return expression.left


def term_action(term):
    import pudb;pudb.set_trace()
    if term.op == '*':
        return term.left * term.right
    elif term.op == '/':
        return term.left / term.right
    else:
        return term.left


def factor_action(factor):
    value = factor.op
    return -value if factor.sign == '-' else value


def operand_action(operand):
    op = operand.op
    if type(op) is text:
        if op in namespace:
            return namespace[op]
        else:
            raise Exception('Unknown variable "{}" at position {}'
                            .format(op, operand._tx_position))
    else:
        return op


def main(debug=False):

    processors = {
        'Calc': calc_action,
        'Assignment': assignment_action,
        'Expression': expression_action,
        'Term': term_action,
        'Factor': factor_action,
        'Operand': operand_action
    }

    calc_mm = metamodel_from_str(grammar, debug=debug)
    calc_mm.register_obj_processors(processors)

    input_expr = '''
        a = 10;
        b = 2 * a + 17;
        -(4-1)*a+(2+4.67)+b*5.89/(.2+7)
    '''

    result = calc_mm.model_from_str(input_expr)

    assert (result - 6.93805555) < 0.0001
    print("Result is", result)


if __name__ == '__main__':
    main()
