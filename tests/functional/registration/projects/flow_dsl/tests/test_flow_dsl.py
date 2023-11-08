import os

import pytest

from textx import (
    TextXSemanticError,
    TextXSyntaxError,
    clear_language_registrations,
    metamodel_for_language,
)

current_dir = os.path.dirname(__file__)


@pytest.fixture(scope="module")
def clear_all():
    clear_language_registrations()


def test_flow_dsl(clear_all):
    """
    Test loading of correct flow model.
    """

    mmF = metamodel_for_language("flow-dsl")
    model = mmF.model_from_file(os.path.join(current_dir, "models", "data_flow.eflow"))
    assert model is not None
    assert len(model.algos) == 2
    assert len(model.flows) == 1


def test_flow_dsl_validation(clear_all):
    """
    Test flow model with semantic error raises error.
    """

    mmF = metamodel_for_language("flow-dsl")
    with pytest.raises(TextXSemanticError, match=r".*algo data types must match.*"):
        mmF.model_from_file(
            os.path.join(current_dir, "models", "data_flow_with_error.eflow")
        )


def test_flow_dsl_types_validation(clear_all):
    """
    Test flow model including error raises error.
    """

    mmF = metamodel_for_language("flow-dsl")
    with pytest.raises(TextXSyntaxError, match=r".*lowercase.*"):
        mmF.model_from_file(
            os.path.join(current_dir, "models", "data_flow_including_error.eflow")
        )

    # When reading a second time, the error must be reported again:

    with pytest.raises(TextXSyntaxError, match=r".*lowercase.*"):
        mmF.model_from_file(
            os.path.join(current_dir, "models", "data_flow_including_error.eflow")
        )
