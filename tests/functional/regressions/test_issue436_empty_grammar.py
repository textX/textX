import pytest

from textx import metamodel_from_str
from textx.exceptions import TextXSyntaxError


def test_empty_grammar_not_allowed():
    """
    Test that textX reports syntax error instead of failing with IndexError.
    Issue reported in https://github.com/textX/textX/issues/436
    """

    with pytest.raises(TextXSyntaxError):
        metamodel_from_str("")
