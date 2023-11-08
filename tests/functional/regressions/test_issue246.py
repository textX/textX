from textx import metamodel_from_str


def test_multiple_rule_modifiers():
    """
    Test that multiple rule modifiers are applied correctly.
    See: https://github.com/textX/textX/issues/246
    """

    grammar = r"""
    main_rule[ws=' \t']:
        "word1" rule1
    ;

    rule1[skipws, ws=' \t\n']:
        "word2" "word3"
    ;
    """

    meta = metamodel_from_str(grammar)
    s = """word1 word2
    word3"""

    model = meta.model_from_str(s)
    assert model == "word1word2word3"
