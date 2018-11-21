from __future__ import unicode_literals
from textx import metamodel_from_str


def test_int_and_floats():
    grammar = r'''
    Model: vars+=Var;
    Var: name=ID '=' value=Val;
    Val: O_FLOAT|O_INT; // order matters: float first!
    O_INT: intVal=MYINT;
    O_FLOAT: floatVal=MYFLOAT;
    MYINT: /\-?\d+/;
    MYFLOAT: /\-?\d+.\d+([eE][-+]?\d+)?/;
    '''
    model_text = '''
    x1 = 1
    x2 = -1
    y1 = 1.0
    y2 = 1.1e-2
    y3 = -1.1e+2
    '''

    mm = metamodel_from_str(grammar)
    mm.register_obj_processors({
        "MYINT": lambda x: int(x),
        "MYFLOAT": lambda x: float(x)
    })
    m = mm.model_from_str(model_text)

    assert 'O_INT' == m.vars[0].value.__class__.__name__
    assert 'O_INT' == m.vars[1].value.__class__.__name__
    assert 'O_FLOAT' == m.vars[2].value.__class__.__name__
    assert 'O_FLOAT' == m.vars[3].value.__class__.__name__
    assert 'O_FLOAT' == m.vars[4].value.__class__.__name__

    assert 1 == m.vars[0].value.intVal
    assert -1 == m.vars[1].value.intVal
    assert abs(1.0 - m.vars[2].value.floatVal) < 1e-5
    assert abs(1.1e-2 - m.vars[3].value.floatVal) < 1e-5
    assert abs(-1.1e+2 - m.vars[4].value.floatVal) < 1e-5
