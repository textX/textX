"""
Tests for issue: https://github.com/textX/textX/issues/357
Inconsistent multiplicity of attributes with multiple assignment.
"""

from textx import metamodel_from_str


def test_multiplicity_with_multiple_assignments_in_ordered_choice():
    """
    When an attribute appears in multiple assignments in an ordered choice
    followed by another assignment in the parent sequence, the multiplicity
    should be "1..*".
    Grammar: (a='a'|a='b') a='c'
    """
    grammar = r"""
    Model: (a='a' | a='b') a='c' 'end';
    """
    mm = metamodel_from_str(grammar)
    attr = mm["Model"]._tx_attrs["a"]
    assert attr.mult == "1..*", (
        f"Expected multiplicity '1..*' for attribute 'a' with multiple "
        f"assignments across ordered choice and sequence, got '{attr.mult}'"
    )


def test_multiplicity_with_same_attr_in_different_oc_branches():
    """
    When an attribute appears in different branches of an ordered choice,
    and also in a sequential assignment, multiplicity should be "1..*".
    """
    grammar = r"""
    Model: (a='x' | a='y' | a='z') a='w' 'end';
    """
    mm = metamodel_from_str(grammar)
    attr = mm["Model"]._tx_attrs["a"]
    assert attr.mult == "1..*", (
        f"Expected multiplicity '1..*' for attribute 'a', got '{attr.mult}'"
    )


def test_multiplicity_with_same_attr_only_in_oc():
    """
    When an attribute appears in multiple branches of an ordered choice
    but not in the parent sequence, multiplicity should remain "1"
    (only one branch can match).
    """
    grammar = r"""
    Model: (a='x' | a='y' | a='z') 'end';
    """
    mm = metamodel_from_str(grammar)
    attr = mm["Model"]._tx_attrs["a"]
    assert attr.mult == "1", (
        f"Expected multiplicity '1' for attribute 'a' (only in OC), "
        f"got '{attr.mult}'"
    )


def test_multiplicity_with_separate_attrs_in_oc():
    """
    When different attributes appear in different OC branches, no
    multiplicity change should happen.
    """
    grammar = r"""
    Model: (a='x' | b='y') a='z' 'end';
    """
    mm = metamodel_from_str(grammar)
    attr_a = mm["Model"]._tx_attrs["a"]
    assert attr_a.mult == "1..*", (
        f"Expected multiplicity '1..*' for attribute 'a' (from OC + seq), "
        f"got '{attr_a.mult}'"
    )


def test_multiplicity_with_plain_sequence():
    """
    The existing behavior: two sequential assignments of the same attribute
    should give multiplicity "1..*".
    """
    grammar = r"""
    Model: a='x' a='y' 'end';
    """
    mm = metamodel_from_str(grammar)
    attr = mm["Model"]._tx_attrs["a"]
    assert attr.mult == "1..*", (
        f"Expected multiplicity '1..*' for attribute 'a' with sequential "
        f"assignments, got '{attr.mult}'"
    )
