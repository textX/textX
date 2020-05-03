from __future__ import unicode_literals
from textx import (metamodel_from_str)
import os.path
from pytest import raises
from textx.exceptions import TextXError


grammar = r"""
Model: 'MyModel' name=ID;
"""

text = r"""
MyModel test1
"""


def test_model_params():
    mm = metamodel_from_str(grammar)
    mm._tx_model_param_definitions.add(
        "parameter1", "an example param (1)"
    )
    mm._tx_model_param_definitions.add(
        "parameter2", "an example param (2)"
    )

    m = mm.model_from_str(text, parameter1='P1', parameter2='P2')
    assert m.name == 'test1'
    assert hasattr(m, '_tx_model_params')
    assert len(m._tx_model_params) == 2
    assert len(m._tx_model_params.used_keys) == 0

    assert not m._tx_model_params.all_used

    assert m._tx_model_params['parameter1'] == 'P1'
    assert len(m._tx_model_params.used_keys) == 1
    assert 'parameter1' in m._tx_model_params.used_keys
    assert 'parameter2' not in m._tx_model_params.used_keys

    assert not m._tx_model_params.all_used

    assert m._tx_model_params['parameter2'] == 'P2'
    assert len(m._tx_model_params.used_keys) == 2
    assert 'parameter1' in m._tx_model_params.used_keys
    assert 'parameter2' in m._tx_model_params.used_keys

    assert m._tx_model_params.all_used

    assert m._tx_model_params.get(
        'missing_params', default='default value') == 'default value'
    assert m._tx_model_params.get(
        'parameter1', default='default value') == 'P1'

    with raises(TextXError, match=".*unknown parameter myerror2.*"):
        mm.model_from_str(text, parameter1='P1', myerror2='P2')

    assert len(mm._tx_model_param_definitions) == 2
    assert mm._tx_model_param_definitions[
               'parameter1'].description == "an example param (1)"


def test_model_params_empty():
    mm = metamodel_from_str(grammar)
    mm._tx_model_param_definitions.add(
        "parameter1", "an example param (1)"
    )
    mm._tx_model_param_definitions.add(
        "parameter2", "an example param (2)"
    )

    m = mm.model_from_str(text)
    assert m.name == 'test1'
    assert hasattr(m, '_tx_model_params')
    assert len(m._tx_model_params) == 0

    assert m._tx_model_params.all_used


def test_model_params_file_based():
    mm = metamodel_from_str(grammar)
    mm._tx_model_param_definitions.add(
        "parameter1", "an example param (1)"
    )
    mm._tx_model_param_definitions.add(
        "parameter2", "an example param (2)"
    )

    current_dir = os.path.dirname(__file__)
    m = mm.model_from_file(
        os.path.join(current_dir, 'test_model_params',
                     'model.txt'),
        parameter1='P1', parameter2='P2')
    assert m.name == 'file_based'
    assert hasattr(m, '_tx_model_params')
    assert len(m._tx_model_params) == 2
