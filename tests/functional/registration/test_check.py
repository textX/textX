"""
Test check/validation command.
"""
import os
import subprocess

this_folder = os.path.abspath(os.path.dirname(__file__))


def test_check_metamodel():
    """
    Meta-model is also a model
    """

    metamodel_file = os.path.join(this_folder,
                                  'projects', 'flow_dsl', 'flow_dsl', 'Flow.tx')
    output = subprocess.check_output(['textx', 'check', metamodel_file],
                                     stderr=subprocess.STDOUT)
    assert b'Flow.tx: OK.' in output


def test_check_valid_model():
    metamodel_file = os.path.join(this_folder,
                                  'projects', 'flow_dsl', 'tests',
                                  'models', 'data_flow.eflow')
    output = subprocess.check_output(['textx', 'check', metamodel_file],
                                     stderr=subprocess.STDOUT)
    assert b'data_flow.eflow: OK.' in output


def test_check_invalid_model():
    metamodel_file = os.path.join(this_folder,
                                  'projects', 'flow_dsl', 'tests',
                                  'models', 'data_flow_including_error.eflow')
    output = subprocess.check_output(['textx', 'check', metamodel_file],
                                     stderr=subprocess.STDOUT)
    assert b'error: types must be lowercase' in output
