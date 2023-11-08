import os.path

import pytest

from textx import metamodel_for_language
from textx.exceptions import TextXError

current_dir = os.path.dirname(__file__)


def test_issue196_errors_in_scope_provider_and_obj_processor():
    mmF = metamodel_for_language("flow-dsl")

    # print("-----------------------------------1---")
    # print(metamodel_for_language('flow-dsl').
    #      _tx_model_repository.all_models.filename_to_model.keys())

    cached_model_count = len(
        metamodel_for_language("flow-dsl")._tx_model_repository.all_models
    )

    with pytest.raises(TextXError, match=r".*types must be lowercase.*"):
        mmF.model_from_file(
            os.path.join(current_dir, "models", "MODEL_WITH_IMPORT_ERROR.eflow")
        )

    # print("-----------------------------------2---")
    # print(metamodel_for_language('flow-dsl').
    #      _tx_model_repository.all_models.filename_to_model.keys())

    # error while reading, no file cached (cached_model_count unchanged)!
    assert cached_model_count == len(
        metamodel_for_language("flow-dsl")._tx_model_repository.all_models
    )

    with pytest.raises(TextXError, match=r'.*Unknown object "A" of class "Algo".*'):
        print("loading MODEL_WITH_TYPE_ERROR")
        mmF.model_from_file(
            os.path.join(current_dir, "models", "MODEL_WITH_TYPE_ERROR.eflow")
        )

    # print("-----------------------------------3---")
    # print(metamodel_for_language('flow-dsl').
    #      _tx_model_repository.all_models.filename_to_model.keys())

    # error while reading, no file cached! (cached_model_count unchanged)!
    assert cached_model_count == len(
        metamodel_for_language("flow-dsl")._tx_model_repository.all_models
    )

    with pytest.raises(TextXError, match=r".*types must be lowercase.*"):
        mmF.model_from_file(
            os.path.join(current_dir, "models", "MODEL_WITH_IMPORT_ERROR.eflow")
        )

    # error while reading, no file cached! (cached_model_count unchanged)!
    assert cached_model_count == len(
        metamodel_for_language("flow-dsl")._tx_model_repository.all_models
    )


def test_issue196_syntax_error_1():
    mmF = metamodel_for_language("flow-dsl")

    # print("-----------------------------------1---")
    # print(metamodel_for_language('flow-dsl').
    #      _tx_model_repository.all_models.filename_to_model.keys())

    cached_model_count = len(
        metamodel_for_language("flow-dsl")._tx_model_repository.all_models
    )

    with pytest.raises(TextXError, match=r".*\d+: Expected.*"):
        mmF.model_from_file(
            os.path.join(current_dir, "models", "MODEL_WITH_IMPORT_SYNTAX_ERROR.eflow")
        )

    # print("-----------------------------------2---")
    # print(metamodel_for_language('flow-dsl').
    #      _tx_model_repository.all_models.filename_to_model.keys())

    # error while reading, no file cached!
    assert cached_model_count == len(
        metamodel_for_language("flow-dsl")._tx_model_repository.all_models
    )


def test_issue196_syntax_error_2():
    mmF = metamodel_for_language("flow-dsl")

    # print("-----------------------------------1---")
    # print(metamodel_for_language('flow-dsl').
    #      _tx_model_repository.all_models.filename_to_model.keys())

    cached_model_count = len(
        metamodel_for_language("flow-dsl")._tx_model_repository.all_models
    )

    with pytest.raises(TextXError, match=r".*\d+: Expected.*"):
        mmF.model_from_file(
            os.path.join(current_dir, "models", "MODEL_WITH_SYNTAX_ERROR.eflow")
        )

    # print("-----------------------------------2---")
    # print(metamodel_for_language('flow-dsl').
    #      _tx_model_repository.all_models.filename_to_model.keys())

    # error while reading, no file cached! (cached_model_count unchanged)!
    assert cached_model_count == len(
        metamodel_for_language("flow-dsl")._tx_model_repository.all_models
    )
