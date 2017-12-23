from os.path import dirname, join
from textx import metamodel_from_file
import os
import textx.scoping as scoping


class Sum(object):
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self,k, v)

class Mul(object):
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self,k, v)

class Factor(object):
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self,k, v)

class ScalarRef(object):
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self,k, v)

def get_meta_model(debug=False):
    this_folder = dirname(__file__)
    mm = metamodel_from_file( os.path.join(os.path.abspath(this_folder),'CustomIDL.tx'), debug=debug,
                              classes=[Sum,Mul,Factor,ScalarRef])
    mm.register_scope_provider({
        "*.*": scoping.ScopeProviderFullyQualifiedNamesWithImportURI(),
        "ScalarRef.ref0": scoping.ScopeProviderForSimpleRelativeNamedLookups("parent(Struct).attributes"),
        "ScalarRef.ref1": scoping.ScopeProviderForSimpleRelativeNamedLookups("ref0.type.attributes"),
        "ScalarRef.ref2": scoping.ScopeProviderForSimpleRelativeNamedLookups("ref1.type.attributes"),
    })
    return mm
