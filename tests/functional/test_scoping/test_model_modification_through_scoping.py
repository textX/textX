from pytest import raises

import textx.scoping.providers as providers
from textx import get_metamodel, get_model, metamodel_from_str
from textx.exceptions import TextXSemanticError
from textx.scoping import Postponed

"""
This test and example demonstrates how to use a custom scope provider to
create an object if a referenced object is not found in the model. See #167.

Here we can
 * define persons and
 * we can specify that persons know each other

The goal is that we can use a custom scope provider to define a known
person on the fly, if it is not define.

If you have additional rules with references to a person, which are not
defining such persons on the fly, you need to take into account, that
some persons may still be generated. Thus, you need to wait (with a
"Postponed" object) for your reference resolution (see grammar_addon and
"Postponer" how this can be achieved).
"""

grammar = r"""
Model: (persons+=Person|knows+=Knows)*;
Person: ':' 'person' name=ID;
Knows: person1=[Person] 'knows' person2=[Person];
"""
grammar_addon = r"""
Model: (persons+=Person|knows+=Knows|greetings=Greeting)*;
Person: ':' 'person' name=ID;
Knows: person1=[Person] 'knows' person2=[Person]; // inventing
Greeting: '*' 'hello' person=[Person]; // non-inventing
"""


def person_definer_scope(knows, attr, attr_ref):
    m = get_model(knows)  # get the model of the currently processed element
    name = attr_ref.obj_name  # the name of currently looked up element
    found_persons = list(filter(lambda p: p.name == name, m.persons))
    if len(found_persons) > 0:
        return found_persons[0]  # if a person exists, return it
    else:
        mm = get_metamodel(m)  # else, create it and store it in the model
        person = mm["Person"]()
        person.name = name
        person.parent = m
        m.persons.append(person)
        return person


class Postponer:
    """
    scope provider which forwards to a base scope provider
    and transforms a None to a Postponed.
    Reference resolution will fail if a set of Postponed
    resolutions does not change any more.
    """

    def __init__(self, base=None):
        if base is None:
            base = providers.PlainName()
        self.base = base

    def __call__(self, *args, **kwargs):
        ret = self.base(*args, **kwargs)
        if ret is None:
            return Postponed()
        else:
            return ret


def test_model_modification_through_scoping_normal_lookup():
    mm = metamodel_from_str(grammar)
    m = mm.model_from_str(
        r"""
        :person Tom
        :person Jerry
        Tom knows Jerry
        """
    )
    assert len(m.persons) == 2
    assert len(m.knows) == 1


def test_model_modification_through_scoping_normal_lookup_failure():
    mm = metamodel_from_str(grammar)
    with raises(TextXSemanticError):
        mm.model_from_str(
            r"""
            :person Tom
            :person Jerry
            Tom knows Jerry
            Tom knows Berry
            """
        )


def test_model_modification_through_scoping_custom_lookup():
    mm = metamodel_from_str(grammar)
    mm.register_scope_providers({"Knows.*": person_definer_scope})
    m = mm.model_from_str(
        r"""
        :person Tom
        :person Jerry
        Tom knows Jerry
        Tom knows Berry
        Berry knows Jerry
        """
    )
    assert len(m.persons) == 3
    assert len(m.knows) == 3

    m = mm.model_from_str(
        r"""
        :person Tom
        :person Jerry
        :person Berry
        Tom knows Jerry
        Tom knows Berry
        Berry knows Jerry
        """
    )
    assert len(m.persons) == 3
    assert len(m.knows) == 3

    m = mm.model_from_str(
        r"""
        Tom knows Jerry
        Tom knows Berry
        Berry knows Jerry
        :person Tom
        :person Jerry
        :person Berry
        """
    )
    assert len(m.persons) == 3
    assert len(m.knows) == 3

    m = mm.model_from_str(
        r"""
        Tom knows Jerry
        Tom knows Berry
        Berry knows Jerry
        """
    )
    assert len(m.persons) == 3
    assert len(m.knows) == 3


def test_model_modification_through_scoping_custom_lookup_addon_failure():
    mm = metamodel_from_str(grammar_addon)
    mm.register_scope_providers({"Knows.*": person_definer_scope})

    # Here, at least one case produces an error, since
    # Tom is not part of the model until the "Knowns" rule
    # is resolved.
    with raises(TextXSemanticError, match=r".*Unknown object.*Tom.*"):
        mm.model_from_str(
            r"""
            Tom knows Jerry
            *hello Tom
            """
        )
        mm.model_from_str(
            r"""
            *hello Tom
            Tom knows Jerry
            """
        )


def test_model_modification_through_scoping_custom_lookup_addon_fix():
    mm = metamodel_from_str(grammar_addon)
    mm.register_scope_providers(
        {"Knows.*": person_definer_scope, "Greeting.*": Postponer()}
    )

    m = mm.model_from_str(
        r"""
        Tom knows Jerry
        *hello Tom
        """
    )

    assert len(m.persons) == 2
    assert len(m.knows) == 1
    assert len(m.greetings) == 1
    assert m.greetings[0].person == m.knows[0].person1

    m = mm.model_from_str(
        r"""
        *hello Tom
        Tom knows Jerry
        """
    )

    assert len(m.persons) == 2
    assert len(m.knows) == 1
    assert len(m.greetings) == 1
    assert m.greetings[0].person == m.knows[0].person1

    # Unknown elements still produce an error, as expected
    with raises(TextXSemanticError, match=r".*Unresolvable.*Berry.*"):
        mm.model_from_str(
            r"""
            Tom knows Jerry
            *hello Berry
            """
        )
