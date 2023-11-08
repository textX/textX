"""
Testing model and object processors.
"""
import pytest  # noqa
from textx.metamodel import metamodel_from_str


class OuterObject:
    counter = 0

    def __init__(self, parent=None, col_items=None):
        print("INIT OuterObject")
        self.col_items = col_items

    def process(self):
        OuterObject.counter += 1
        print("PROCESS OuterObject")


class InnerObject:
    counter = 0

    def __init__(self, parent=None, m_id=None):
        print("INIT InnerObject")
        self.m_id = m_id

    def process(self):
        print("PROCESS InnerObject")
        InnerObject.counter += 1


grammar1 = """
OuterObject:
    col_items += BreakingObject[',']
;

BreakingObject:
    InnerObject
;

InnerObject:
    m_id=STRING
;

"""

grammar2 = """
OuterObject:
    col_items += InnerObject[',']
;

InnerObject:
    m_id=STRING
;

"""


def default_processor(obj):
    obj.process()


def parse_lola(grammar, lola_str):
    lola_str = lola_str
    obj_processors = {"InnerObject": default_processor, "OuterObject": default_processor}

    lola_classes = [InnerObject, OuterObject]

    meta_model = metamodel_from_str(
        grammar, classes=lola_classes, ignore_case=True, auto_init_attributes=False
    )
    meta_model.register_obj_processors(obj_processors)
    model = meta_model.model_from_str(lola_str)
    return model


def test_issue72():
    test_str = "'foo', 'bar'"

    OuterObject.counter = 0
    InnerObject.counter = 0
    parse_lola(grammar2, test_str)
    assert OuterObject.counter == 1
    assert InnerObject.counter == 2

    OuterObject.counter = 0
    InnerObject.counter = 0
    parse_lola(grammar1, test_str)
    assert OuterObject.counter == 1
    assert InnerObject.counter == 2  # fails (issue 72)
