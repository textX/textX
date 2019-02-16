from __future__ import unicode_literals

from textx import metamodel_from_str, get_model, get_metamodel
from pytest import raises
from textx.exceptions import TextXSemanticError

"""
This test and example demonstrates how to use a custom scope provider to
create an object if a referenced object is not found in the model. See #167.

Here we can
 * define persons and
 * we can specify that persons know each other

The goal is that we can use a custom scope provider to define a known
person on the fly, if it is not define.

Note: This example has some limits. Another scope provider which requires to
reference a person not yet created, may get an error.
"""

grammar = r'''
Model: (persons+=Person|knows+=Knows)*;
Person: ':' 'person' name=ID;
Knows: person1=[Person] 'knows' person2=[Person];
'''


def person_definer_scope(knows, attr, attr_ref):
    m = get_model(knows)  # get the model of the currently processed element
    name = attr_ref.obj_name  # the name of currently looked up element
    found_persons = list(filter(lambda p: p.name == name, m.persons))
    if len(found_persons) > 0:
        return found_persons[0]  # if a person exists, return it
    else:
        mm = get_metamodel(m)  # else, create it and store it in the model
        person = mm['Person']()
        person.name = name
        person.parent = m
        m.persons.append(person)
        return person


def test_issue167_normal_lookup():
    mm = metamodel_from_str(grammar)
    m = mm.model_from_str(r'''
        :person Tom
        :person Jerry
        Tom knows Jerry
        ''')
    assert len(m.persons) == 2
    assert len(m.knows) == 1


def test_issue167_normal_lookup_failure():
    mm = metamodel_from_str(grammar)
    with raises(TextXSemanticError):
        mm.model_from_str(r'''
            :person Tom
            :person Jerry
            Tom knows Jerry
            Tom knows Berry
            ''')


def test_issue167_custom_lookup():
    mm = metamodel_from_str(grammar)
    mm.register_scope_providers({'Knows.*': person_definer_scope})
    m = mm.model_from_str(r'''
        :person Tom
        :person Jerry
        Tom knows Jerry
        Tom knows Berry
        Berry knows Jerry
        ''')
    assert len(m.persons) == 3
    assert len(m.knows) == 3

    mm = metamodel_from_str(grammar)
    mm.register_scope_providers({'Knows.*': person_definer_scope})
    m = mm.model_from_str(r'''
        :person Tom
        :person Jerry
        :person Berry
        Tom knows Jerry
        Tom knows Berry
        Berry knows Jerry
        ''')
    assert len(m.persons) == 3
    assert len(m.knows) == 3

    mm = metamodel_from_str(grammar)
    mm.register_scope_providers({'Knows.*': person_definer_scope})
    m = mm.model_from_str(r'''
        Tom knows Jerry
        Tom knows Berry
        Berry knows Jerry
        :person Tom
        :person Jerry
        :person Berry
        ''')
    assert len(m.persons) == 3
    assert len(m.knows) == 3

    mm = metamodel_from_str(grammar)
    mm.register_scope_providers({'Knows.*': person_definer_scope})
    m = mm.model_from_str(r'''
        Tom knows Jerry
        Tom knows Berry
        Berry knows Jerry
        ''')
    assert len(m.persons) == 3
    assert len(m.knows) == 3
