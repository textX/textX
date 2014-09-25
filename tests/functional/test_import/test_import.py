import pytest
import os

from textx.metamodel import metamodel_from_file
from textx.export import metamodel_export, model_export


def test_import():
    """
    Test grammar import.
    """

    current_dir = os.path.dirname(__file__)
    mm = metamodel_from_file(os.path.join(current_dir, 'first.tx'))
    metamodel_export(mm, 'import_test_mm.dot')

    model = """
    first
        second "1" "2"
        third true false true 12 false
    endfirst
    """

    model = mm.model_from_str(model)
    model_export(model, 'import_test_model.dot')

