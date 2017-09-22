from __future__ import unicode_literals
import pytest  # noqa

from textx.metamodel import metamodel_from_str
from textx.export import metamodel_export, model_export


def test_issue_14():
    """
    Test object processors in context of match rules with base types.
    """

    grammar = """
        Program:
        'begin'
            commands*=Command
        'end'
        ;

        Command:
        InitialCommand | InteractCommand
        ;

        InitialCommand:
        'initial' x=INT ',' y=INT
        ;

        InteractCommand:
            'sleep' | INT | FLOAT | BOOL | STRING
        ;
    """

    mm = metamodel_from_str(grammar)
    metamodel_export(mm, 'test_issue_14_metamodel.dot')

    # Error happens only when there are obj. processors registered
    mm.register_obj_processors({'InitialCommand': lambda x: x})

    model_str = """
        begin
            initial 2, 3
            sleep
            34
            4.3
            true
            "a string"
        end
    """
    model = mm.model_from_str(model_str)
    model_export(model, 'test_issue_14_model.dot')
