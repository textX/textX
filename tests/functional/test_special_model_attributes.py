from __future__ import unicode_literals
import pytest
import os
from textx.metamodel import metamodel_from_str


metamodel_str = '''
    Root:
        objs+=MyObj[',']
    ;
    MyObj:
        val=INT
    ;
'''


def test_special_model_attributes():

    this_folder = os.path.abspath(os.path.dirname(__file__))
    mm = metamodel_from_str(metamodel_str)
    model = mm.model_from_file(
        os.path.join(this_folder, 'test_special_model_attributes.model'))

    assert model._tx_filename
    assert model._tx_filename.endswith('test_special_model_attributes.model')
    assert model._tx_metamodel is mm
    assert model.objs[1]._tx_position is 4

    model = mm.model_from_str('34, 56')

    assert model._tx_filename is None
    assert model._tx_metamodel is mm
    assert model.objs[1]._tx_position is 4
