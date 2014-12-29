import pytest
from textx.metamodel import metamodel_from_str
from textx.exceptions import TextXSyntaxError


def test_ignore_case():
    pass


def test_skipws():
    pass


def test_ws():
    pass


def test_autokwd():
    """
    Test that string matches match the whole words.
    """
    langdef = """
    Model: 'start' rules*='first' 'firstsecond';
    """
    meta = metamodel_from_str(langdef)

    # If autokwd is disabled (default) zeroormore will
    # consume all 'first's.
    with pytest.raises(TextXSyntaxError):
        model = meta.model_from_str('start first first firstsecond')

    meta = metamodel_from_str(langdef, autokwd=True)
    model = meta.model_from_str('start first first firstsecond')
    assert model
    assert hasattr(model, 'rules')
    assert len(model.rules) == 2
    assert model.rules[1] == 'first'


