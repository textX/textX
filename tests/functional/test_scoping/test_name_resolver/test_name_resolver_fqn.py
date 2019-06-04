from __future__ import unicode_literals
import textx.scoping.providers as scoping_providers
from textx import metamodel_from_str
from textx.scoping.tools import textx_isinstance
from textx.scoping import Postponed
from os.path import dirname, join

mygrammar = r'''
Model:
        imports*=Import
        packages*=Package
;
Package:
        'package' name=ID '{'
        (
        packages+=Package
        |
        components+=Component
        |
        instances+=Instance
        )+
        '}'
;

// if unnamed, gets name "unnamed_<idx>"
Component:
    'component' (name=ID)? ";"
;

Instance:
    'instance' name=ID ':' component=[Component|FQN];

Import: "import" importURI=STRING;
FQN: ID+['.'];
Comment: /\/\/.*$/;
'''

mymodel1text = r'''
package p1 {
  component unnamed_0;
  component unnamed_1;
  component unnamed_4;

  package p2 {
    component unnamed_2;
    component unnamed_3;
    package p3 {
       component; // unnamed_0
       component; // unnamed_1
       component; // unnamed_2

       instance i0: unnamed_0
       instance i1: unnamed_1
       instance i2: unnamed_2
       instance i3: unnamed_3 // from p2
       instance i4: unnamed_4 // from p1
    }
  }
}
'''

this_folder = dirname(__file__)
_postpone_level = 0
_postpone_counter = 0
_mm = None


def _my_name_resolver_component(obj):
    global _mm
    global _postpone_counter
    global _postpone_level

    if hasattr(obj, "name") and len(obj.name) > 0:
        return scoping_providers.default_name_resolver(
            obj)
    elif textx_isinstance(obj, _mm["Component"]):
        idx = obj.parent.components.index(obj)
        if idx <= _postpone_level:
            return "unnamed_{}".format(idx)
        else:
            _postpone_counter += 1
            _postpone_level += 1
            return Postponed()
    else:
        return scoping_providers.default_name_resolver(
            obj)


def test_name_resolver_postponed_fqn_and_multiple_names_on_different_levels():
    global _mm
    global _postpone_counter
    global _postpone_level

    _mm = metamodel_from_str(mygrammar)
    _postpone_level = 0
    _postpone_counter = 0

    _mm.register_scope_providers({
        "*.*": scoping_providers.FQN(
            name_resolver=_my_name_resolver_component),
    })

    model1 = _mm.model_from_str(mymodel1text)

    assert _postpone_counter == 2

    p1 = model1.packages[0]
    p2 = p1.packages[0]
    p3 = p2.packages[0]

    # check note
    assert p3.instances[0].component == p3.components[0]
    assert p3.instances[1].component == p3.components[1]
    assert p3.instances[2].component == p3.components[2]
    assert p3.instances[3].component == p2.components[1]
    assert p3.instances[4].component == p1.components[2]


def test_name_resolver_postponed_fqn_and_importURI():
    global _mm
    global _postpone_counter
    global _postpone_level

    _mm = metamodel_from_str(mygrammar)
    _postpone_level = 0
    _postpone_counter = 0

    _mm.register_scope_providers({
        "*.*": scoping_providers.FQNImportURI(
            name_resolver=_my_name_resolver_component),
    })

    model1 = _mm.model_from_file(join(this_folder, "file1.model"))

    assert _postpone_counter == 3  # unnamed_3 from file2.model

    p1 = model1.packages[0]
    p2 = p1.packages[0]
    p3 = p2.packages[0]

    other_p1 = model1.imports[0]._tx_loaded_models[0].packages[0]

    # check note
    assert p3.instances[0].component == p3.components[0]
    assert p3.instances[1].component == p3.components[1]
    assert p3.instances[2].component == p3.components[2]
    assert p3.instances[3].component == p2.components[1]
    assert p3.instances[4].component == p1.components[2]
    assert p3.instances[5].component == p1.components[2]
    assert p3.instances[6].component == p1.components[0]
    assert p3.instances[7].component == other_p1.components[3]
