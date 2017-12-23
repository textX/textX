from os.path import dirname, join
from textx import metamodel_from_file
import os
import textx.scoping as scoping


class CustomIdlBase(object):
    def __init__(self):
        pass

    def _init_xtextobj(self, **kwargs):
        for k in kwargs.keys():
            setattr(self, k, kwargs[k])

class FormulaBase(CustomIdlBase):
    def __init__(self):
        super(CustomIdlBase, self).__init__()

    def render_formula(self):
        raise Exception("base class - not implmented")

class Sum(FormulaBase):
    def __init__(self, **kwargs):
        super(FormulaBase,self).__init__()
        self._init_xtextobj(**kwargs)

    def render_formula(self):
        return "+".join( map(lambda x:x.render_formula(), self.summands) )


class Mul(FormulaBase):
    def __init__(self, **kwargs):
        super(FormulaBase, self).__init__()
        self._init_xtextobj(**kwargs)

    def render_formula(self):
        return "*".join( map(lambda x:x.render_formula(), self.factors) )


class Factor(FormulaBase):
    def __init__(self, **kwargs):
        super(FormulaBase, self).__init__()
        self._init_xtextobj(**kwargs)

    def render_formula(self):
        if self.ref:
            return self.ref.render_formula()
        elif self.sum:
            return "({})".format(self.sum.render_formula())
        else:
            return "{}".format(self.value)


class ScalarRef(FormulaBase):
    def __init__(self, **kwargs):
        super(FormulaBase, self).__init__()
        self._init_xtextobj(**kwargs)

    def render_formula(self):
        return ".".join(map(lambda x: x.name,
                            filter(lambda x: x,
                                   [self.ref0, self.ref1, self.ref2])))

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
