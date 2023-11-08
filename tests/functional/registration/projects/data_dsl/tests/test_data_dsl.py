import os

from textx import clear_language_registrations, metamodel_for_language


def test_data_dsl():
    """
    Test loading of correct data dsl.
    """

    clear_language_registrations()
    current_dir = os.path.dirname(__file__)
    mmD = metamodel_for_language("data-dsl")
    model = mmD.model_from_file(
        os.path.join(current_dir, "models", "data_structures.edata")
    )
    assert model is not None
    assert len(model.data) == 3
