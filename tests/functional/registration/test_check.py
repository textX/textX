"""
Test check/validation command.
"""
import os

from click.testing import CliRunner
from pytest import raises

from textx.cli import textx
from textx.exceptions import TextXSyntaxError
from textx.registration import metamodel_for_language

this_folder = os.path.abspath(os.path.dirname(__file__))


def test_object_processor_with_optional_parameter_default():
    mm = metamodel_for_language("types-dsl")
    model_file = os.path.join(
        this_folder, "projects", "types_dsl", "tests", "models", "types_with_error.etype"
    )
    with raises(TextXSyntaxError, match="types must be lowercase"):
        mm.model_from_file(model_file)


def test_object_processor_with_optional_parameter_on():
    mm = metamodel_for_language("types-dsl")
    model_file = os.path.join(
        this_folder, "projects", "types_dsl", "tests", "models", "types_with_error.etype"
    )
    with raises(TextXSyntaxError, match="types must be lowercase"):
        mm.model_from_file(model_file, type_name_check="on")


def test_object_processor_with_optional_parameter_off():
    mm = metamodel_for_language("types-dsl")
    model_file = os.path.join(
        this_folder, "projects", "types_dsl", "tests", "models", "types_with_error.etype"
    )
    mm.model_from_file(model_file, type_name_check="off")


def test_check_metamodel():
    """
    Meta-model is also a model.
    """

    metamodel_file = os.path.join(
        this_folder, "projects", "flow_dsl", "flow_dsl", "Flow.tx"
    )
    runner = CliRunner()
    result = runner.invoke(textx, ["check", metamodel_file])
    assert result.exit_code == 0
    assert "Flow.tx: OK." in result.output


def test_check_valid_model():
    model_file = os.path.join(
        this_folder, "projects", "flow_dsl", "tests", "models", "data_flow.eflow"
    )
    runner = CliRunner()
    result = runner.invoke(textx, ["check", model_file])
    assert result.exit_code == 0
    assert "data_flow.eflow: OK." in result.output


def test_check_valid_model_with_explicit_language_name():
    """
    Test checking of model where language name is given explicitly.
    """
    model_file = os.path.join(
        this_folder, "projects", "flow_dsl", "tests", "models", "data_flow.eflow"
    )
    runner = CliRunner()
    result = runner.invoke(textx, ["check", "--language", "flow-dsl", model_file])
    assert result.exit_code == 0
    assert "data_flow.eflow: OK." in result.output


def test_check_valid_model_with_metamodel_from_file():
    """
    Test checking of model where meta-model is provided from the grammar file.
    """
    model_file = os.path.join(
        this_folder, "projects", "types_dsl", "tests", "models", "types.etype"
    )
    metamodel_file = os.path.join(
        this_folder, "projects", "types_dsl", "types_dsl", "Types.tx"
    )
    runner = CliRunner()
    result = runner.invoke(textx, ["check", "--grammar", metamodel_file, model_file])
    assert result.exit_code == 0
    assert "types.etype: OK." in result.output


def test_check_invalid_model():
    model_file = os.path.join(
        this_folder,
        "projects",
        "flow_dsl",
        "tests",
        "models",
        "data_flow_including_error.eflow",
    )
    runner = CliRunner()
    result = runner.invoke(textx, ["check", model_file])
    assert result.exit_code != 0
    assert "Error:" in result.output
    assert "types must be lowercase" in result.output


def test_check_invalid_language():
    """
    Test calling check command with a file that is not registered.
    """

    runner = CliRunner()
    result = runner.invoke(textx, ["check", "some_unexisting_file"])

    assert "No language registered that can parse" in result.output
