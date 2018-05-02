"""
Testing model and object processors.
"""
from __future__ import unicode_literals
import pytest  # noqa
import sys
from textx import metamodel_from_str

if sys.version < '3':
    text = unicode  # noqa
else:
    text = str

grammar = """
First:
    'first' seconds+=Second
    ('A' a+=INT)?
    ('B' b=BOOL)?
    ('C' c=STRING)?
;

Second:
    sec = INT
;

"""

model_processor_called = False


def test_model_processor():
    """
    Test that model processors are called after model parsing.
    """
    global model_processor_called

    model_str = 'first 34 45 7 A 45 65 B true C "dfdf"'

    metamodel = metamodel_from_str(grammar)
    metamodel.register_model_processor(model_processor)

    metamodel.model_from_str(model_str)

    assert model_processor_called


def model_processor(model, metamodel):
    """
    Model processor is called when the model is successfully parsed.
    """
    global model_processor_called
    model_processor_called = True

    assert model.__class__.__name__ == "First"
    assert model.seconds[0].sec == 34


def test_object_processors():
    """
    Test that object processors are called.
    They should be called after each model object construction.
    """

    call_order = []

    def first_obj_processor(first):
        first._first_called = True
        call_order.append(1)

    def second_obj_processor(second):
        second._second_called = True
        call_order.append(2)

        # test that parent is fully initialised.
        # b should be True
        assert second.parent.b

    obj_processors = {
        'First': first_obj_processor,
        'Second': second_obj_processor,
        }

    metamodel = metamodel_from_str(grammar)
    metamodel.register_obj_processors(obj_processors)

    model_str = 'first 34 45 7 A 45 65 B true C "dfdf"'
    first = metamodel.model_from_str(model_str)

    assert hasattr(first, '_first_called')
    for s in first.seconds:
        assert hasattr(s, '_second_called')
    assert call_order == [2, 2, 2, 1]


def test_object_processor_replace_object():
    """
    Test that what is returned from object processor is value used in the
    output model.
    """
    def second_obj_processor(second):
        return second.sec / 2

    def string_obj_processor(mystr):
        return "[{}]".format(mystr)

    obj_processors = {
        'Second': second_obj_processor,
        'STRING': string_obj_processor,
        }

    metamodel = metamodel_from_str(grammar)
    metamodel.register_obj_processors(obj_processors)

    model_str = 'first 34 45 7 A 45 65 B true C "dfdf"'
    first = metamodel.model_from_str(model_str)

    assert len(first.seconds) == 3
    assert first.seconds[0] == 17

    assert first.c == '[dfdf]'


def test_obj_processor_simple_match_rule():
    grammar = """
    First:
        a=MyFloat 'end'
    ;
    MyFloat:
        /\d+\.(\d+)?/
    ;
    """
    model = '3. end'

    mm = metamodel_from_str(grammar)
    m = mm.model_from_str(model)
    assert type(m.a) is text

    processors = {
        'MyFloat': lambda x: float(x)
    }
    print('filters')
    mm = metamodel_from_str(grammar)
    mm.register_obj_processors(processors)
    m = mm.model_from_str(model)

    assert type(m.a) is float


def test_obj_processor_sequence_match_rule():

    grammar = """
    First:
        i=MyFixedInt 'end'
    ;
    MyFixedInt:
    '0' '0' '04'
    ;
    """

    model = '0004 end'

    mm = metamodel_from_str(grammar)
    m = mm.model_from_str(model)
    assert type(m.i) is text

    processors = {
        'MyFixedInt': lambda x: int(x)
    }
    mm = metamodel_from_str(grammar)
    mm.register_obj_processors(processors)
    m = mm.model_from_str(model)

    assert type(m.i) is int


def test_base_type_obj_processor_override():
    grammar = """
    First:
        'begin' i=INT 'end'
    ;
    """

    processors = {
        'INT': lambda x: float(x)
    }
    mm = metamodel_from_str(grammar)
    mm.register_obj_processors(processors)
    m = mm.model_from_str('begin 34 end')

    assert type(m.i) is float
