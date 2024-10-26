from os.path import dirname, join

from textx import metamodel_from_str
from textx.export import metamodel_export, model_export

grammar = '''
Bool: assignments*=Assignment expression=Or;
Assignment: variable=ID '=' expression=Or';';
Or: op=And ('or' op=And)*;
And: op=Not ('and' op=Not)*;
Not: _not?='not' op=Operand;
Operand: op=BOOL | op=ID | ( '(' op=Or ')' );
'''

# Global variable namespace
namespace = {}


class Bool:
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


class Or(ExpressionElement):
    @property
    def value(self):
        ret = self.op[0].value
        for operand in self.op[1:]:
            ret = ret or operand.value
        return ret


class And(ExpressionElement):
    @property
    def value(self):
        ret = self.op[0].value
        for operand in self.op[1:]:
            ret = ret and operand.value
        return ret


class Not(ExpressionElement):
    def __init__(self, **kwargs):
        self._not = kwargs.pop('_not')
        super().__init__(**kwargs)

    @property
    def value(self):
        ret = self.op.value
        return not ret if self._not else ret


class Operand(ExpressionElement):
    @property
    def value(self):
        op = self.op
        if isinstance(op, bool):
            return op
        elif op in namespace:
            return namespace[op]
        else:
            raise Exception(f'Unknown variable "{op}" at position {self._tx_position}'
                            )


def main(debug=False):

    bool_mm = metamodel_from_str(grammar,
                                 classes=[Bool, Or, And, Not, Operand],
                                 ignore_case=True,
                                 debug=debug)

    this_folder = dirname(__file__)
    if debug:
        metamodel_export(bool_mm, join(this_folder, 'bool_metamodel.dot'))

    input_expr = '''
        a = true;
        b = not a and true;
        a and false or not b
    '''

    model = bool_mm.model_from_str(input_expr)

    if debug:
        model_export(model, join(this_folder, 'bool_model.dot'))

    # Getting value property from the Bool instance will start evaluation.
    result = model.value

    assert model.value is True
    print("Result is", result)


if __name__ == '__main__':
    main()
