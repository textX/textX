from __future__ import unicode_literals
from pytest import raises
import os
from textx import TextXSyntaxError, metamodel_for_language


def test_types_dsl():
    mmT = metamodel_for_language('types-dsl')
    current_dir = os.path.dirname(__file__)
    model = mmT.model_from_file(os.path.join(current_dir,
                                             'models',
                                             'types.etype'))
    assert(model is not None)
    assert(len(model.types) == 2)


def test_types_dsl_valid():
    mmT = metamodel_for_language('types-dsl')
    current_dir = os.path.dirname(__file__)
    with raises(TextXSyntaxError,
                match=r'.*lowercase.*'):
        mmT.model_from_file(os.path.join(current_dir,
                                         'models',
                                         'types_with_error.etype'))
