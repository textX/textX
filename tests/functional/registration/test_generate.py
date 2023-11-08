"""
Tests for `generate` command.
"""
import os
from contextlib import suppress

import pytest
from click.testing import CliRunner

from textx.cli import textx

this_folder = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def model_file():
    with suppress(OSError):
        os.remove(
            os.path.join(
                this_folder, "projects", "flow_dsl", "tests", "models", "data_flow.pu"
            )
        )

    return os.path.join(
        this_folder, "projects", "flow_dsl", "tests", "models", "data_flow.eflow"
    )


def test_generator_registered():
    """
    That that generator from flow to PlantUML is registered
    """
    runner = CliRunner()
    result = runner.invoke(textx, ["list-generators"])
    assert result.exit_code == 0
    assert "flow-dsl -> PlantUML" in result.output


def test_generating_flow_model(model_file):
    """
    Test that generator can be called.
    """
    runner = CliRunner()
    result = runner.invoke(
        textx, ["generate", "--target", "PlantUML", "--overwrite", model_file]
    )
    assert result.exit_code == 0
    assert "Generating PlantUML target from models" in result.output
    assert "->" in result.output
    assert "models/data_flow.pu" in result.output
    assert os.path.exists(
        os.path.join(
            this_folder, "projects", "flow_dsl", "tests", "models", "data_flow.pu"
        )
    )


def test_generate_by_providing_explicit_language_name(model_file):
    """
    Test running generator by providing an explicit language name.
    """
    runner = CliRunner()
    result = runner.invoke(
        textx,
        [
            "generate",
            "--language",
            "flow-dsl",
            "--target",
            "PlantUML",
            "--overwrite",
            model_file,
        ],
    )
    assert result.exit_code == 0
    assert "Generating PlantUML target from models" in result.output
    assert "->" in result.output
    assert "models/data_flow.pu" in result.output
    assert os.path.exists(
        os.path.join(
            this_folder, "projects", "flow_dsl", "tests", "models", "data_flow.pu"
        )
    )


def test_passing_custom_arguments_to_generator(model_file):
    """
    Test passing custom arguments from command line to the generator.
    """
    runner = CliRunner()
    result = runner.invoke(
        textx,
        [
            "generate",
            "--language",
            "flow-dsl",
            "--target",
            "PlantUML",
            model_file,
            "--custom1",
            "42",
            "--custom2",
            '"some string"',
            "--overwrite",
        ],
    )
    assert result.exit_code == 0
    assert "Generating PlantUML target from models" in result.output
    assert "->" in result.output
    assert "models/data_flow.pu" in result.output
    target_file = os.path.join(
        this_folder, "projects", "flow_dsl", "tests", "models", "data_flow.pu"
    )
    assert os.path.exists(target_file)
    with open(target_file) as f:
        content = f.read()
    assert "custom1=42" in content
    assert "custom2=some string" in content


def test_generate_for_invalid_file_raises_error():
    """
    Test running generator by providing an explicit language name.
    """
    runner = CliRunner()
    result = runner.invoke(
        textx,
        ["generate", "--target", "PlantUML", "--overwrite", "unexistingmodel.invalid"],
    )

    assert "No language registered that can parse" in result.output
