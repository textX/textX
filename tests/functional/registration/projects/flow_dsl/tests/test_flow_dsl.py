from __future__ import unicode_literals
import os
from pytest import raises
from textx import TextXSemanticError, TextXSyntaxError, metamodel_for_language


def test_flow_dsl():
    mmF = metamodel_for_language('flow-dsl')
    current_dir = os.path.dirname(__file__)
    model = mmF.model_from_file(os.path.join(current_dir,
                                             'models',
                                             'data_flow.eflow'))
    assert(model is not None)
    assert(len(model.algos) == 2)
    assert(len(model.flows) == 1)


def test_flow_dsl_validation():
    mmF = metamodel_for_language('flow-dsl')
    current_dir = os.path.dirname(__file__)
    with raises(TextXSemanticError,
                match=r'.*algo data types must match.*'):
        mmF.model_from_file(os.path.join(current_dir,
                                         'models',
                                         'data_flow_with_error.eflow'))


def test_flow_dsl_types_validation():
    mmF = metamodel_for_language('flow-dsl')
    current_dir = os.path.dirname(__file__)
    current_dir = os.path.dirname(__file__)
    with raises(TextXSyntaxError,
                match=r'.*lowercase.*'):
        mmF.model_from_file(os.path.join(current_dir,
                                         'models',
                                         'data_flow_including_error.eflow'))
