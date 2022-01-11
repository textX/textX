"""
Problem with TextXMetaMetamodel model params definition.
https://github.com/textX/textX/issues/360
"""
from textx.metamodel import TextXMetaMetaModel


def test_textxmetametamodel_has_model_param_defs():
    assert hasattr(TextXMetaMetaModel(), "model_param_defs")
