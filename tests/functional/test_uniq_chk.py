import pytest

from textx import metamodel_from_str
from textx.uniq_chk import uniq_chk
from textx.exceptions import TextXSemanticError


# adapter from entity example
grammar = """
EntityModel:
    entities+=Entity
;

Entity:
    'entity' name=ID '{'
        properties*=Property
    '}'
;

Type:
    'int' | 'string' | 'float'
;

Property:
    name=ID ':' type=Type
;
"""


def uniq_chk_entities(x):
    uniq_chk(x, 'entities')


def uniq_chk_properties(x):
    uniq_chk(x, 'properties')


def test_multiple_objects_model_level():
    """
    Test that model children uniqueness is validated.
    """
    metamodel = metamodel_from_str(grammar)
    metamodel.register_obj_processors({
        'EntityModel': uniq_chk_entities,
        })

    model_str1 = 'entity A {} entity B {} entity A {}'
    model_str2 = 'entity A {} entity A {} entity B {}'
    model_str3 = 'entity A {} entity A {} entity A {}'

    # TODO test specific error message
    for model_str in [model_str1, model_str2, model_str3]:
        with pytest.raises(TextXSemanticError):
            metamodel.model_from_str(model_str)


def test_multiple_objects_inner_level():
    """
    Test that model grand-children uniqueness is validated.
    """
    metamodel = metamodel_from_str(grammar)
    metamodel.register_obj_processors({
        'Entity': uniq_chk_properties,
        })

    model_str1 = """
        entity A {
            name : string
            age : int
            name : float
        }
        """

    model_str2 = """
        entity A {
            name : string
            age : int
        }

        entity B {
            name : string
            age : int
            age : int
            age : int
        }
    """

    # TODO test specific error message
    for model_str in [model_str1, model_str2]:
        with pytest.raises(TextXSemanticError):
            metamodel.model_from_str(model_str)
