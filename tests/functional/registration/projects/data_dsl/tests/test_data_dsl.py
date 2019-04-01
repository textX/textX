from __future__ import unicode_literals
from textx import metamodel_for_language
import os


def test_data_dsl():
    mmD = metamodel_for_language('data-dsl')
    current_dir = os.path.dirname(__file__)
    model = mmD.model_from_file(os.path.join(current_dir,
                                             'models',
                                             'data_structures.edata'))
    assert(model is not None)
    assert(len(model.data) == 3)
