from __future__ import unicode_literals
import pytest  # noqa
import os
from textx import metamodel_from_str, metamodel_from_file

grammar = """
First:
    'first' seconds+=Second
;

Second:
    value=INT
;

"""


def test_textx_metaclass_repr():
    """
    Test metaclass __repr__
    """

    metamodel = metamodel_from_str(grammar)
    assert '<textx:First class at' in repr(metamodel['First'])


def test_textx_metaclass_instance_repr():
    """
    Test metaclass instance __repr__
    """

    metamodel = metamodel_from_str(grammar)
    model = metamodel.model_from_str('first 42')
    assert '<textx:First instance at' in repr(model)


def test_textx_imported_metaclass_repr():
    """
    Test imported metaclass __repr__ uses fqn.
    """

    current_dir = os.path.dirname(__file__)
    mm = metamodel_from_file(os.path.join(current_dir, 'import',
                                          'first_diamond.tx'))
    MyDiamondRule = mm['diamond.last.MyDiamondRule']

    assert '<textx:diamond.last.MyDiamondRule class at' in repr(MyDiamondRule)


def test_textx_imported_metaclass_instance_repr():
    """
    Test imported metaclass instance __repr__ uses fqn.
    """

    current_dir = os.path.dirname(__file__)
    mm = metamodel_from_file(os.path.join(current_dir, 'import',
                                          'first_diamond.tx'))
    model = mm.model_from_str('second 42 11 third 42')

    assert '<textx:diamond.last.MyDiamondRule instance at' \
        in repr(model.seconds[0].diamond)


def test_textx_imported_metaclass_repr_same_level_import():
    current_dir = os.path.dirname(__file__)
    mm = metamodel_from_file(os.path.join(current_dir, 'import',
                                          'repr',
                                          'first_repr.tx'))
    model = mm.model_from_str('second 42')

    assert '<textx:third_repr.Third instance at' \
        in repr(model.seconds[0].thirds[0])

def test_textx_circular_abstract_rules():
    import textx

    METAMODEL = textx.metamodel_from_str("""
    Model: expression=Expr ;

    ParenExpr: '(' Expr ')';
    Expr: ParenExpr | BaseExpr;
    BaseExpr: left=Condition operations*=Operation;
    Operation:  op=BoolOperator remaining=Condition;

    Condition: ParenExpr | RawCondition;
    RawCondition: id=Identifier op=MathOperator val=INT;

    Identifier: id=/[a-zA-Z0-9_-]+/;
    MathOperator:  op=/=|>|</;
    BoolOperator:  op=/AND|OR/;
    """)

    from textx.scoping.tools import textx_isinstance

    m1 = METAMODEL.model_from_str('(b=3 OR c=4)')
    assert textx_isinstance(m1.expression, METAMODEL['BaseExpr'])
    assert textx_isinstance(m1.expression.left, METAMODEL['RawCondition'])
    assert len(m1.expression.operations) == 1
    assert m1.expression.operations[0].op.op == 'OR'
    assert textx_isinstance(m1.expression.operations[0].remaining, METAMODEL['RawCondition'])

    m2 = METAMODEL.model_from_str('a=2 AND (b=3 OR c=4)')
    assert textx_isinstance(m2.expression, METAMODEL['BaseExpr'])
    assert textx_isinstance(m2.expression.left, METAMODEL['RawCondition'])
    assert len(m2.expression.operations) == 1
    assert m2.expression.operations[0].op.op == 'AND'
    assert textx_isinstance(m2.expression.operations[0].remaining, METAMODEL['BaseExpr'])
    assert textx_isinstance(m2.expression.operations[0].remaining.left, METAMODEL['RawCondition'])
    assert len(m2.expression.operations[0].remaining.operations)==1
    assert m2.expression.operations[0].remaining.operations[0].op.op == 'OR'
    assert textx_isinstance(m2.expression.operations[0].remaining.operations[0].remaining, METAMODEL['RawCondition'])

