from __future__ import unicode_literals
import textx.scoping.providers as scoping_providers
from textx import metamodel_from_str
from textx.scoping.tools import textx_isinstance, resolve_model_path
from textx.scoping import Postponed

mygrammar = r'''
Model:
        packages*=Package
;
Package:
        'package' name=ID '{'
        (
        components+=Component
        |
        instances+=Instance
        |
        connections+=Connection
        |
        packages+=Package
        |
        interfaces+=Interface
        |
        notes+=ConnectionNote
        )*
        '}'
;

Interface: 'interface' name=ID;

// A component defines something with in/out ports
// A component can inherit form another component --> lookup with inheritance
Component:
    'component' name=ID ('extends' extends+=[Component|FQN][','])? '{'
        slots*=Slot
    '}'
;

Slot: SlotIn|SlotOut;

// name of slot deduced (if not specified) by name resolver
// "(IN|OUT)_index"
SlotIn:
    'in' (name=ID)?
    ('(' 'format' formats+=[Interface|FQN][','] ')')
;
SlotOut:
    'out' (name=ID)?
    ('(' 'format' formats+=[Interface|FQN][','] ')')
;

Instance:
    'instance' name=ID ':' component=[Component|FQN] ;

// name of connection deduced via name resolver
// "from_inst.name" + "_" + "from_port.name" + "_to_"
// + "to_inst.name" + "_" + "to_port.name"
// (Parts of the name can be postponed).
Connection:
    'connect'
      from_inst=[Instance|ID] '.' from_port=[SlotOut|ID]
    'to'
      to_inst=[Instance|ID] '.' to_port=[SlotIn|ID]
;

ConnectionNote: 'note' 'for' connection=[Connection] ':' text=STRING;

FQN: ID+['.'];
Comment: /\/\/.*$/;
'''

mymodel1text = r'''
package interfaces {
  interface B
  interface C
}
package base {
  interface A
  interface D
  component Start {
    out output1 (format A) // OUT_0
    out (format interfaces.B) // OUT_1
    out (format interfaces.C) // OUT_2
  }
  component Middle extends Start, End {
    in (format A,interfaces.B,interfaces.C) // IN_0
    out (format interfaces.B,interfaces.C,D) // hides OUT_1 from Start
  }
  component End {
    in input3 (format interfaces.B,interfaces.C,D)
  }
}

package usage {
  instance start : base.Start
  instance action1 : base.Middle
  instance action2 : base.Middle
  instance action3 : base.Middle
  instance end : base.End

  connect start.output1   to action1.IN_0
  connect start.OUT_1   to action1.IN_0 // OUT_0 form Middle  **line1**
  connect action1.OUT_1 to action2.input3 // OUT_1 from Start
  connect action2.OUT_1 to action3.IN_0 // OUT_0 from Middle
  connect action3.OUT_1 to end.input3

  note for start_OUT_1_to_action1_IN_0 : "note for connections[1]"
}
'''


def test_name_resolver_basic_functionality():
    mm = metamodel_from_str(mygrammar)

    def my_name_resolver_slots(obj):
        if hasattr(obj, "name") and len(obj.name) > 0:
            return scoping_providers.default_name_resolver(
                obj)
        elif textx_isinstance(obj, mm["SlotIn"]):
            idx = obj.parent.slots.index(obj)
            return "IN_{}".format(idx)
        elif textx_isinstance(obj, mm["SlotOut"]):
            idx = obj.parent.slots.index(obj)
            return "OUT_{}".format(idx)
        else:
            return scoping_providers.default_name_resolver(
                obj)

    def my_name_resolver_fqn(obj):
        if textx_isinstance(obj, mm["Connection"]):
            from_inst = resolve_model_path(obj, "from_inst")
            from_port = resolve_model_path(obj, "from_port")
            to_inst = resolve_model_path(obj, "to_inst")
            to_port = resolve_model_path(obj, "to_port")
            if type(from_inst) is Postponed or\
                    type(from_port) is Postponed or\
                    type(to_inst) is Postponed or\
                    type(to_port) is Postponed:
                return Postponed()
            #
            # !! Here we need to check if the port names
            # are postponed, too.
            # We also need to invoke the other name resolver
            # manually.
            #
            from_port_name = my_name_resolver_slots(from_port)
            to_port_name = my_name_resolver_slots(to_port)
            if type(from_port_name) is Postponed or\
                    type(to_port_name) is Postponed:
                return Postponed()
            return "{}_{}_to_{}_{}".format(
                from_inst.name, from_port_name,
                to_inst.name, to_port_name,
            )
        else:
            return scoping_providers.default_name_resolver(
                obj)

    mm.register_scope_providers({
        "*.*": scoping_providers.FQN(name_resolver=my_name_resolver_fqn),
        "Connection.from_port":
            scoping_providers.ExtRelativeName(
                "from_inst.component",
                "slots",
                "extends",
                name_resolver=my_name_resolver_slots),
        "Connection.to_port":
            scoping_providers.ExtRelativeName(
                "to_inst.component",
                "slots",
                "extends",
                name_resolver=my_name_resolver_slots),
    })

    model1 = mm.model_from_str(mymodel1text)

    # check note
    assert model1.packages[2].notes[0].connection\
        == model1.packages[2].connections[1]

    # check **line1**
    assert model1.packages[2].connections[1].from_port\
        == model1.packages[1].components[0].slots[1]
    assert model1.packages[2].connections[1].to_port\
        == model1.packages[1].components[1].slots[0]
