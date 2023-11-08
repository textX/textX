import os

import pytest

from textx import metamodel_from_file, metamodel_from_str
from textx.export import metamodel_export, model_export


def test_import():
    """
    Test grammar import.
    """

    current_dir = os.path.dirname(__file__)
    mm = metamodel_from_file(os.path.join(current_dir, "relativeimport", "first.tx"))
    metamodel_export(mm, "import_test_mm.dot")

    model = """
    first
        second "1" "2"
        third true false true 12 false
    endfirst
    """

    model = mm.model_from_str(model)
    model_export(model, "import_test_model.dot")


def test_multiple_imports():
    """
    Test that grammar rules imported from multiple places
    results in the same meta-class objects.
    """

    current_dir = os.path.dirname(__file__)
    mm = metamodel_from_file(os.path.join(current_dir, "multiple", "first.tx"))

    assert (
        mm["First"]._tx_attrs["seconds"].cls._tx_attrs["thirds"].cls
        is mm["relative.third.Third"]
    )
    metamodel_export(mm, "multipleimport_test_mm.dot")

    model = """
        first 1 2
        third "one" "two"
    """

    model = mm.model_from_str(model)
    model_export(model, "multipleimport_test_model.dot")


def test_no_import_for_string():
    """
    Test that import can't be used if meta-model is loaded from string.
    """

    grammar = """
    import relativeimport.first

    Second:
        a = First
    ;

    """

    with pytest.raises(AssertionError):
        metamodel_from_str(grammar)
