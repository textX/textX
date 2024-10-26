from os.path import dirname, join

from textx import metamodel_from_str
from textx.export import metamodel_export, model_export

grammar = '''
Calc: assignments*=Assignment expression=Expression;
Assignment: variable=ID '=' expression=Expression ';';
Expression: op=Term (op=PlusOrMinus op=Term)* ;
PlusOrMinus: '+' | '-';
Term: op=Factor (op=MulOrDiv op=Factor)*;
MulOrDiv: '*' | '/' ;
Factor: (sign=PlusOrMinus)?  op=Operand;
Operand: op=NUMBER | op=ID | ('(' op=Expression ')');
'''

# Global variable namespace
namespace = {}


class Calc:
    def __init__(self, **kwargs):
        self.assignments = kwargs.pop('assignments')
        self.expression = kwargs.pop('expression')

    @property
    def value(self):
        # Evaluate variables in the order of definition
        for a in self.assignments:
            namespace[a.variable] = a.expression.value
        return self.expression.value


class ExpressionElement:
    def __init__(self, **kwargs):

        # textX will pass in parent attribute used for parent-child
        # relationships. We can use it if we want to.
        self.parent = kwargs.get('parent')

        # We have 'op' attribute in all grammar rules
        self.op = kwargs['op']

        super().__init__()


class Factor(ExpressionElement):
    def __init__(self, **kwargs):
        self.sign = kwargs.pop('sign', '+')
        super().__init__(**kwargs)

    @property
    def value(self):
        value = self.op.value
        return -value if self.sign == '-' else value


class Term(ExpressionElement):
    @property
    def value(self):
        ret = self.op[0].value
        for operation, operand in zip(self.op[1::2], self.op[2::2]):
            if operation == '*':
                ret *= operand.value
            else:
                ret /= operand.value
        return ret


class Expression(ExpressionElement):
    @property
    def value(self):
        ret = self.op[0].value
        for operation, operand in zip(self.op[1::2], self.op[2::2]):
            if operation == '+':
                ret += operand.value
            else:
                ret -= operand.value
        return ret


class Operand(ExpressionElement):
    @property
    def value(self):
        op = self.op
        if type(op) in {int, float}:
            return op
        elif isinstance(op, ExpressionElement):
            return op.value
        elif op in namespace:
            return namespace[op]
        else:
            raise Exception(f'Unknown variable "{op}" at position {self._tx_position}'
                            )


def main(debug=False):

    calc_mm = metamodel_from_str(grammar,
                                 classes=[Calc, Expression, Term, Factor,
                                          Operand],
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

    # Getting value property from the Calc instance will start evaluation.
    result = model.value

    assert (model.value - 6.93805555) < 0.0001
    print("Result is", result)


if __name__ == '__main__':
    main()
