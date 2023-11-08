import pytest

from textx import metamodel_from_str
from textx.exceptions import TextXSemanticError


def test_unhashable_type_for_name():
    """
    Test that using unhashable type for name of model object is correctly reported.
    """

    mm = metamodel_from_str(
        """
    TestObj: name+=ID['.'];
    """
    )

    with pytest.raises(TextXSemanticError, match=".*of unhashable type.*"):
        mm.model_from_str("test")
