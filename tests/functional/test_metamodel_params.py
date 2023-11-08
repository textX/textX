import pytest

from textx import metamodel_from_str
from textx.exceptions import TextXSyntaxError


def test_ignore_case():
    langdef = """
    Model: 'start' rules*='first' 'second';
    """
    meta = metamodel_from_str(langdef)

    # By default case is not ignored.
    with pytest.raises(TextXSyntaxError):
        meta.model_from_str("Start first First Second")

    meta = metamodel_from_str(langdef, ignore_case=True)
    meta.model_from_str("Start first First Second")


def test_skipws():
    langdef = """
    Model: 'start' rules*='first' 'second';
    """
    meta = metamodel_from_str(langdef)

    # By default ws are skipped.
    meta.model_from_str("start first first second")

    meta = metamodel_from_str(langdef, skipws=False)
    with pytest.raises(TextXSyntaxError):
        meta.model_from_str("start first first second")

    meta.model_from_str("startfirstfirstsecond")


def test_ws():
    langdef = """
    Model: 'start' rules*='first' 'second';
    """
    meta = metamodel_from_str(langdef)

    # Default ws are space, tab and newline
    meta.model_from_str(
        """start  first 
            first second"""
    )  # noqa

    meta = metamodel_from_str(langdef, ws=" ")
    with pytest.raises(TextXSyntaxError):
        meta.model_from_str(
            """start  first 
                first second"""
        )  # noqa

    meta.model_from_str("start first first second")


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
        model = meta.model_from_str("start first first firstsecond")

    meta = metamodel_from_str(langdef, autokwd=True)
    model = meta.model_from_str("start first first firstsecond")
    assert model
    assert hasattr(model, "rules")
    assert len(model.rules) == 2
    assert model.rules[1] == "first"
