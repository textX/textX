"""
Testing model and object processors.
"""
import pytest
from textx.metamodel import metamodel_from_str

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

