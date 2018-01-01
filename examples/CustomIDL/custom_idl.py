from os.path import dirname
from textx import metamodel_from_file, children_of_type, model_root
import os
import textx.scoping as scoping
import textx.scoping_tools as scoping_tools
from functools import reduce


class CustomIdlBase(object):
    def __init__(self):
        pass

    def _init_xtextobj(self, **kwargs):
        for k in kwargs.keys():
            setattr(self, k, kwargs[k])


class RawType(CustomIdlBase):
    def __init__(self, **kwargs):
        super(CustomIdlBase, self).__init__()
        self._init_xtextobj(**kwargs)


class Struct(CustomIdlBase):
    def __init__(self, **kwargs):
        super(CustomIdlBase, self).__init__()
        self._init_xtextobj(**kwargs)

    def get_structs_of_attributes(self):
        result = set()
        for s in filter(lambda x: type(x) is Struct, map(lambda x: x.type, self.attributes)):
            result.add(s)
        return result

    def get_raw_types_of_attributes(self):
        result = set()
        for s in filter(lambda x: type(x) is RawType, map(lambda x: x.type, self.attributes)):
            result.add(s)
        return result


class ScalarAttribute(CustomIdlBase):
    def __init__(self, **kwargs):
        super(CustomIdlBase, self).__init__()
        self._init_xtextobj(**kwargs)

    def affects_size(self):
        struct = scoping_tools.get_recursive_parent_with_typename(self, "Struct")
        for a in filter(lambda x: type(x) is ArrayAttribute, struct.attributes):
            for s in a.array_sizes:
                for ref in children_of_type("ScalarRef", s):
                    if self is ref.ref0:
                        return True
        return False


class ArrayAttribute(CustomIdlBase):
    def __init__(self, **kwargs):
        super(CustomIdlBase, self).__init__()
        self._init_xtextobj(**kwargs)

    def has_fixed_size(self):
        return reduce( lambda x,y: x and y, map(lambda x: x.has_fixed_size(), self.array_sizes), True )

def check_scalar_ref(scalar_ref):
    def myassert(ref):
        assert ref.default_value, "{}: {}.{} needs to have a default value".format(model_root(ref)._tx_filename,ref.parent.name,ref.name)
    if scalar_ref.ref2:
        myassert(scalar_ref.ref2)
    elif scalar_ref.ref1:
        myassert(scalar_ref.ref1)
    else:
        myassert(scalar_ref.ref0)


def get_meta_model(debug=False):
    from custom_idl_formula import Sum, Mul, Dif, Div, Val, ScalarRef

    this_folder = dirname(__file__)
    mm = metamodel_from_file( os.path.join(os.path.abspath(this_folder),'CustomIDL.tx'), debug=debug,
                              classes=[Sum,Mul,Dif,Div,Val,ScalarRef,RawType,Struct,ArrayAttribute,ScalarAttribute])

    mm.register_scope_provider({
        "*.*": scoping.ScopeProviderFullyQualifiedNamesWithImportURI(),
        "ScalarRef.ref0": scoping.ScopeProviderForSimpleRelativeNamedLookups("parent(Struct).attributes"),
        "ScalarRef.ref1": scoping.ScopeProviderForSimpleRelativeNamedLookups("ref0.type.attributes"),
        "ScalarRef.ref2": scoping.ScopeProviderForSimpleRelativeNamedLookups("ref1.type.attributes"),
    })

    mm.register_obj_processors({
        "ScalarRef": check_scalar_ref
    })

    return mm
