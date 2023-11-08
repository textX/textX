"""
Model query and navigation API.
"""
import pytest  # noqa
from textx import (
    metamodel_from_str,
    get_children,
    get_children_of_type,
    get_parent_of_type,
    get_model,
)


grammar = """
First:
    a+=Second
    b*=Third
;

Second:
    x+=INT[','] (':' y=Third)?
;

Third:
    x=STRING
;
"""


model_str = """
    23, 45, 56 : "one"
    53, 56, 87 : "two"
    23, 45, 77
    "first" "second" "third"
"""


def test_get_children():
    metamodel = metamodel_from_str(grammar)
    model = metamodel.model_from_str(model_str)

    seconds_thirds = get_children(
        lambda x: x.__class__.__name__ in ["Second", "Third"], model
    )

    assert len(seconds_thirds) == 8  # 3 seconds and 5 thirds
    assert seconds_thirds[0].x == [23, 45, 56]
    assert seconds_thirds[1].x == "one"
    assert seconds_thirds[-1].x == "third"

    # Children first
    seconds_thirds = get_children(
        lambda x: x.__class__.__name__ in ["Second", "Third"], model, children_first=True
    )

    assert len(seconds_thirds) == 8  # 3 seconds and 5 thirds
    assert seconds_thirds[0].x == "one"
    assert seconds_thirds[1].x == [23, 45, 56]
    assert seconds_thirds[-1].x == "third"

    # Do not traverse seconds
    seconds_thirds = get_children(
        lambda x: x.__class__.__name__ in ["Second", "Third"],
        model,
        should_follow=lambda x: x.__class__.__name__ != "Second",
    )
    assert len(seconds_thirds) == 3  # Only 3 thirds at the top of the model
    assert seconds_thirds[0].x == "first"
    assert seconds_thirds[-1].x == "third"


def test_get_children_of_type():
    metamodel = metamodel_from_str(grammar)
    model = metamodel.model_from_str(model_str)

    thirds = get_children_of_type("Third", model)
    assert len(thirds) == 5
    assert set(["first", "second", "third", "one", "two"]) == set([a.x for a in thirds])

    # Test search in the part of the model
    thirds = get_children_of_type("Third", model.a[1])
    assert len(thirds) == 1
    assert list(thirds)[0].x == "two"

    # Do not traverse seconds
    thirds = get_children_of_type(
        "Third", model, should_follow=lambda x: x.__class__.__name__ != "Second"
    )
    assert len(thirds) == 3  # Only 3 thirds at the top of the model
    assert thirds[0].x == "first"
    assert thirds[-1].x == "third"


def test_get_parent_of_type():
    metamodel = metamodel_from_str(grammar)
    model = metamodel.model_from_str(model_str)

    t = model.a[0].y
    s = get_parent_of_type("Second", t)
    assert s.__class__.__name__ == "Second"
    assert s.x[0] == 23
    f = get_parent_of_type("First", t)
    assert f.__class__.__name__ == "First"
    assert f is model


def test_get_model():
    metamodel = metamodel_from_str(grammar)
    model = metamodel.model_from_str(model_str)

    t = model.a[0].y
    assert get_model(t) is model
