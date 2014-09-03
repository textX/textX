import pytest
from textx.metamodel import metamodel_from_str


def test_match_whole_word():
    """
    Test that string matches match the whole words.
    """
    langdef = """
    Model: 'start' rules*='first' 'firstsecond';
    """
    meta = metamodel_from_str(langdef)
    model = meta.model_from_str('start first first firstsecond')
    assert model
    assert hasattr(model, 'rules')
    assert len(model.rules) == 2
    assert model.rules[1] == 'first'
