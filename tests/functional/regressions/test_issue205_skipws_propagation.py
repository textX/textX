import pytest

from textx import TextXSyntaxError, metamodel_from_str


def test_issue205_skipws_propagation():
    """
    Test a problem found in Arpeggio not maintaining `skipws/noskipws` applied
    to ordered choice root rule.
    Reported at SO: https://stackoverflow.com/questions/57944531/how-do-you-correctly-mix-textx-skipws-non-skipws
    """  # noqa: E501

    mm = metamodel_from_str(
        r"""
            Sentence[skipws]: words*=Word;
            Word[noskipws]: ID '.' | ID | '.';
        """
    )

    # If ```noskipws``` from the ```Word``` rule is obeyed then this won't
    # parse as there is no rule to consume spaces in between the words. In the
    # unfixed Arpeggio version ```skipws``` from ```Sentence``` would nullify
    # ```noskipws``` from Word so the parse will not fail but it would not be
    # what should be expected.
    with pytest.raises(TextXSyntaxError):
        mm.model_from_str("""foo bar .""")

    # We should consume spaces explicitly. Here, we show that a rule with the
    # ```noskipws``` rule modifier is able to consume spaces explicitly. Match
    # suppression (-) is employed to exclude these spaces from the target value
    # (this means the ```Word``` does not include the spaces in its value).
    # Note: ```skipws``` of Sentence does not consume the spaces between the
    # words, because the rule modifiers
    # (http://textx.github.io/textX/stable/grammar/#rule-modifiers) apply
    # immediately. Thus, we need to consume the extra spaces before a word.
    mm = metamodel_from_str(
        r"""
            Sentence[skipws]: words*=Word;
            Word[noskipws]: /\s*/- (ID '.' | ID | '.');
        """
    )

    m = mm.model_from_str("""foo bar .""")
    assert len(m.words) == 3
