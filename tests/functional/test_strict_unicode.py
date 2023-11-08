import pytest  # noqa
from textx import metamodel_from_str, TextXError


def test_that_passing_a_non_string_raises_exception():
    # Test metamodel construction
    with pytest.raises(TextXError, match=r"textX accepts only strings."):
        metamodel = metamodel_from_str(42)

    metamodel = metamodel_from_str("First: INT;")
    metamodel.model_from_str("42")

    # Test model constuction
    with pytest.raises(TextXError, match=r"textX accepts only strings."):
        metamodel.model_from_str(42)
