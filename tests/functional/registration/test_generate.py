"""
Tests for `generate` command.
"""
import os
from textx.cli import textx
from click.testing import CliRunner

this_folder = os.path.abspath(os.path.dirname(__file__))


def test_generator_registered():
    """
    That that generator from flow to PlantUML is registered
    """
    runner = CliRunner()
    result = runner.invoke(textx, ['list-generators'])
    assert result.exit_code == 0
    assert 'flow-dsl -> PlantUML' in result.output


def test_generating_flow_model():
    """
    Test that generator can be called.
    """
    model_file = os.path.join(this_folder,
                              'projects', 'flow_dsl', 'tests',
                              'models', 'data_flow.eflow')
    runner = CliRunner()
    result = runner.invoke(textx, ['generate', '--target', 'PlantUML',
                                   '--overwrite', model_file])
    assert result.exit_code == 0
    assert 'Generating PlantUML target from models' in result.output
    assert '->' in result.output
    assert 'models/data_flow.pu' in result.output
    assert os.path.exists(os.path.join(this_folder,
                                       'projects', 'flow_dsl', 'tests',
                                       'models', 'data_flow.pu'))
