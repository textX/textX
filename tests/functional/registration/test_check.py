"""
Test check/validation command.
"""
import os
from textx.cli import textx
from click.testing import CliRunner

this_folder = os.path.abspath(os.path.dirname(__file__))


def test_check_metamodel():
    """
    Meta-model is also a model
    """

    metamodel_file = os.path.join(this_folder,
                                  'projects', 'flow_dsl', 'flow_dsl',
                                  'Flow.tx')
    runner = CliRunner()
    result = runner.invoke(textx, ['check', metamodel_file])
    assert result.exit_code == 0
    assert 'Flow.tx: OK.' in result.output


def test_check_valid_model():
    model_file = os.path.join(this_folder,
                              'projects', 'flow_dsl', 'tests',
                              'models', 'data_flow.eflow')
    runner = CliRunner()
    result = runner.invoke(textx, ['check', model_file])
    assert result.exit_code == 0
    assert 'data_flow.eflow: OK.' in result.output


def test_check_invalid_model():
    model_file = os.path.join(this_folder,
                              'projects', 'flow_dsl', 'tests',
                              'models', 'data_flow_including_error.eflow')
    runner = CliRunner()
    result = runner.invoke(textx, ['check', model_file])
    assert result.exit_code == 0
    assert 'error: types must be lowercase' in result.output
