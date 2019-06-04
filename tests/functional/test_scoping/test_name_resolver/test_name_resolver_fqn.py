from __future__ import unicode_literals
import textx.scoping.providers as scoping_providers
from textx import metamodel_from_str
from textx.scoping.tools import textx_isinstance
from textx.scoping import Postponed

mygrammar = r'''
Model:
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
       instance i3: unnamed_4 // from p1
    }
  }
}
'''


postpone_level = 2
postpone_counter = 0


def test_name_resolver_postponed_fqn_and_multiple_names_on_different_levels():
    mm = metamodel_from_str(mygrammar)

    def my_name_resolver_component(obj):
        global postpone_level
        global postpone_counter

        if hasattr(obj, "name") and len(obj.name) > 0:
            return scoping_providers.default_name_resolver(
                obj)
        elif textx_isinstance(obj, mm["Component"]):
            idx = obj.parent.components.index(obj)
            if idx >= postpone_level:
                return "unnamed_{}".format(idx)
            else:
                postpone_counter += 1
                postpone_level -= 1
                return Postponed()
        else:
            return scoping_providers.default_name_resolver(
                obj)

    mm.register_scope_providers({
        "*.*": scoping_providers.FQN(name_resolver=my_name_resolver_component),
    })

    global postpone_counter
    model1 = mm.model_from_str(mymodel1text)

    assert postpone_counter == 2

    p1 = model1.packages[0]
    p2 = p1.packages[0]
    p3 = p2.packages[0]

    # check note
    assert p3.instances[0].component == p3.components[0]
    assert p3.instances[1].component == p3.components[1]
    assert p3.instances[2].component == p3.components[2]
    assert p3.instances[3].component == p2.components[1]
    assert p3.instances[4].component == p1.components[2]
