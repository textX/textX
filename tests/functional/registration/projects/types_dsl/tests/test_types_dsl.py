import os

import pytest

from textx import TextXSyntaxError, clear_language_registrations, metamodel_for_language

current_dir = os.path.dirname(__file__)


@pytest.fixture(scope="module")
def clear_all():
    clear_language_registrations()


def test_types_dsl(clear_all):
    """
    Test loading of correct types model.
    """

    mmT = metamodel_for_language("types-dsl")
    model = mmT.model_from_file(os.path.join(current_dir, "models", "types.etype"))
    assert model is not None
    assert len(model.types) == 2


def test_types_dsl_invalid(clear_all):
    """
    Test that types model with semantic error raises the error.
    """

    mmT = metamodel_for_language("types-dsl")
    with pytest.raises(TextXSyntaxError, match=r".*lowercase.*"):
        mmT.model_from_file(os.path.join(current_dir, "models", "types_with_error.etype"))
