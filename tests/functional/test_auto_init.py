from textx import metamodel_from_str

grammar = """
First:
    dummy=INT
    ('first' seconds+=Second)?
    ('A' a=INT)?
    ('B' b=BOOL)?
    ('C' c=STRING)?
    d?='boolasgn'
    ('F' f=FLOAT)?
;

Second:
    INT|STRING
;

"""


def test_auto_init():
    """
    Test that attributes are initialized to propper
    values if not specified in the model.
    """

    mm = metamodel_from_str(grammar)

    model = mm.model_from_str("42")

    assert model.seconds == []

    # Numeric attributes are initialized to 0
    assert model.a == 0
    assert model.f == 0

    # Boolean attributes are initialized to False
    assert model.b is False
    assert model.d is False

    # String attributes are initialized to ""
    assert model.c == ""


def test_no_auto_init():
    """
    Test that attributes are are initialized if
    auto_init_attributes is set to False.
    """

    mm = metamodel_from_str(grammar, auto_init_attributes=False)

    model = mm.model_from_str("42")

    # Many multiplicity will have python array as value
    assert model.seconds == []

    # All base type attributes will be None
    assert model.a is None
    assert model.b is None
    assert model.c is None
    assert model.f is None

    # But for ?= assignment we will have default value of False
    # because there cannot be three state.
    # Either string to match exists or not.
    assert model.d is False
