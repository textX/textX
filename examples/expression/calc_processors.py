"""
This is a variant of calc example using object processors for on-the-fly
evaluation.
"""
from textx import metamodel_from_str

grammar = '''
Calc: assignments*=Assignment expression=Expression;
Assignment: variable=ID '=' expression=Expression ';';
Expression: operands=Term (operators=PlusOrMinus operands=Term)*;
PlusOrMinus: '+' | '-';
Term: operands=Factor (operators=MulOrDiv operands=Factor)*;
MulOrDiv: '*' | '/' ;
Factor: (sign=PlusOrMinus)?  op=Operand;
Operand: op_num=NUMBER | op_id=ID | ('(' op_expr=Expression ')');
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
            raise Exception(f'Unknown variable "{operand.op_id}" '
                            f'at position {operand._tx_position}')
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
    calc_mm.register_obj_processors(processors)

    input_expr = '''
        a = 10;
        b = 2 * a + 17;
        -(4-1)*a+(2+4.67)+b*5.89/(.2+7)
    '''

    calc = calc_mm.model_from_str(input_expr)
    result = calc.expression

    assert (result - 6.93805555) < 0.0001
    print("Result is", result)


if __name__ == '__main__':
    main()
