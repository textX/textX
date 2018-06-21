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
Model:
    firsts*=First
;
First:
    'first' seconds+=Second
;

Second:
    sec = INT
;

"""

class First:
    def __init__(self, seconds, **kwargs):
        print("INIT First {}".format(str(seconds)))
        self.seconds = seconds

class Second:
    def __init__(self, sec, **kwargs):
        print("INIT Second {}".format(sec))
        self.sec = sec

def test_object_processors2():
    """
    Test that object processors are called.
    """

    metamodel = metamodel_from_str(grammar, classes=[First,Second] )

    first_obj_proc_calls = []
    second_obj_proc_calls = []
    def first_obj_processor(first):
        model_str = 'first 1000 1000'
        if len(first.seconds)>5:
            m2 = metamodel.model_from_str(model_str)
            first_obj_proc_calls.append(m2)

    def second_obj_processor(second):
        model_str = 'first 99 99 {}'.format(100+second.sec)
        if second.sec<50:
            m2 = metamodel.model_from_str(model_str)
            second_obj_proc_calls.append(m2)

    obj_processors = {
        'First': first_obj_processor,
        'Second': second_obj_processor,
        }

    metamodel.register_obj_processors(obj_processors)

    model_str = 'first 1 2 3 4 5 6 7'
    m = metamodel.model_from_str(model_str)

    from textx import get_children_of_type

    f = get_children_of_type('First', m)
    assert len(f)==1
    s = get_children_of_type('Second', m)
    assert len(s)==7

    assert len(first_obj_proc_calls) == 1
    assert len(second_obj_proc_calls) == 7
