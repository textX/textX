import pytest  # noqa
import os
from textx import metamodel_from_str


metamodel_str = """
    Root:
        objs+=MyObj[',']
    ;
    MyObj:
        val=INT
    ;
"""


def test_special_model_attributes():
    this_folder = os.path.abspath(os.path.dirname(__file__))
    mm = metamodel_from_str(metamodel_str)
    model = mm.model_from_file(
        os.path.join(this_folder, "test_special_model_attributes.model")
    )

    assert model._tx_filename
    assert model._tx_filename.endswith("test_special_model_attributes.model")
    assert model._tx_metamodel is mm
    assert model.objs[1]._tx_position == 4

    model = mm.model_from_str("34, 56")

    assert model._tx_filename is None
    assert model._tx_metamodel is mm
    assert model.objs[1]._tx_position == 4
    assert model.objs[1]._tx_position_end == 6

    # Meta-model is also a model. Test classes.
    assert mm["Root"]._tx_position == 5
    assert mm["Root"]._tx_position_end == 41
    assert mm["MyObj"]._tx_position == 46
    assert mm["MyObj"]._tx_position_end == 74
