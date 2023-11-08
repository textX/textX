from textx.metamodel import metamodel_from_str


def xtest_issue206_regex_reference1():
    mm = metamodel_from_str(
        """
        Word: ('bar' /[ ]*/)*;
    """,
        skipws=False,
        debug=False,
    )

    m = mm.model_from_str("""bar bar""", debug=False)
    assert m is not None


def test_issue206_regex():
    mm = metamodel_from_str(
        """
        Word: ('bar' / */)*;
    """,
        skipws=False,
        debug=False,
    )

    m = mm.model_from_str("""bar bar""", debug=False)
    assert m is not None
