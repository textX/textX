"""
Tests for `generate` command.
"""
import os
import subprocess

this_folder = os.path.abspath(os.path.dirname(__file__))


def test_generator_registered():
    """
    That that generator from flow to PlantUML is registered
    """
    output = subprocess.check_output(['textx', 'list-generators'],
                                     stderr=subprocess.STDOUT)
    assert b'flow-dsl -> PlantUML' in output


def test_generating_flow_model():
    """
    Test that generator can be called.
    """
    model_file = os.path.join(this_folder,
                              'projects', 'flow_dsl', 'tests',
                              'models', 'data_flow.eflow')
    output = subprocess.check_output(['textx', 'generate',
                                      '--target', 'PlantUML',
                                      '--overwrite',
                                      model_file],
                                     stderr=subprocess.STDOUT)
    assert b'Generating PlantUML target from models' in output
    assert b'->' in output
    assert b'models/data_flow.pu'
    assert os.path.exists(os.path.join(this_folder,
                                       'projects', 'flow_dsl', 'tests',
                                       'models', 'data_flow.pu'))
