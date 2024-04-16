"""
This is a variant of calc example using dynamically added properties to
classes created by textx.
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


def calc_value(self):
    # Evaluate variables in the order of definition
    for a in self.assignments:
        namespace[a.variable] = a.expression.value
    return self.expression.value


def expression_value(self):
    ret = self.operands[0].value
    for operation, operand in zip(self.operators, self.operands[1:]):
        if operation == '+':
            ret += operand.value
        else:
            ret -= operand.value
    return ret


def term_value(self):
    ret = self.operands[0].value
    for operation, operand in zip(self.operators, self.operands[1:]):
        if operation == '*':
            ret *= operand.value
        else:
            ret /= operand.value
    return ret


def factor_value(self):
    value = self.op.value
    return -value if self.sign == '-' else value


def operand_value(self):
    if self.op_num is not None:
        return self.op_num
    elif self.op_id:
        if self.op_id in namespace:
            return namespace[self.op_id]
        else:
            raise Exception(f'Unknown variable "{self.op_id}" '
                            f'at position {self._tx_position}')
    else:
        return self.op_expr.value


def main(debug=False):

    calc_mm = metamodel_from_str(grammar, auto_init_attributes=False,
                                 debug=debug)

    calc_mm['Calc'].value = property(calc_value)
    calc_mm['Factor'].value = property(factor_value)
    calc_mm['Term'].value = property(term_value)
    calc_mm['Expression'].value = property(expression_value)
    calc_mm['Operand'].value = property(operand_value)

    input_expr = '''
        a = 10;
        b = 2 * a + 17;
        -(4-1)*a+(2+4.67)+b*5.89/(.2+7)
    '''

    model = calc_mm.model_from_str(input_expr)
    result = model.value

    assert (result - 6.93805555) < 0.0001
    print("Result is", result)


if __name__ == '__main__':
    main()
