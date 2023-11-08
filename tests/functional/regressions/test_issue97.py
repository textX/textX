from pytest import raises

import textx


def test_issue97_buildin_NUMBER_as_INT_or_FLOAT():
    """
    see issue 97 for a detailed error report
    """

    mm = textx.metamodel_from_str(
        """
        Model:
          value1=NUMBER value2=NUMBER
        ;
    """
    )

    m = mm.model_from_str(
        """
        10 1.5
    """
    )

    assert isinstance(m.value1, int)
    assert isinstance(m.value2, float)
    assert not isinstance(m.value1, float)
    assert not isinstance(m.value2, int)


def test_issue97_buildin_STRICTFLOAT_as_INT_or_FLOAT():
    """
    see issue 97 for a detailed error report
    """

    mm = textx.metamodel_from_str(
        """
        Model: data+=Data;
        Data: StrictFloat|Float|Int;
        StrictFloat: 's' sfvalue=STRICTFLOAT;
        Float: 'f' fvalue=FLOAT;
        Int: 'i' ivalue=INT;
    """
    )

    mm.model_from_str(
        """
        i1 i2 i3 f1 f2 f3 f1.0 f1. f.1 f1e1
    """
    )

    mm.model_from_str(
        """
        s1.0 s1. s.1 s1e1
        s-1.0 s-1. s-.1 s-1e1
        s-1e-1 s-1.e-1 s-.1e-1
    """
    )

    with raises(textx.exceptions.TextXSyntaxError, match=r".*Expected STRICTFLOAT.*"):
        mm.model_from_str(
            """
            s1
        """
        )
    with raises(textx.exceptions.TextXSyntaxError, match=r".*Expected INT.*"):
        mm.model_from_str(
            """
            i.1
        """
        )
    with raises(
        textx.exceptions.TextXSyntaxError, match=r".*"
    ):  # "i1" is parsed, the ".1" causes an error
        mm.model_from_str(
            """
            i1.1
        """
        )
    with raises(textx.exceptions.TextXSyntaxError, match=r".*"):
        mm.model_from_str(
            """
            i1e1
        """
        )
