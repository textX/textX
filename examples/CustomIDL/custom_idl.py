from os.path import dirname, join
from textx import metamodel_from_file
import os
import textx.scoping as scoping
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

class Attribute(CustomIdlBase):
    def __init__(self, **kwargs):
        super(CustomIdlBase, self).__init__()
        self._init_xtextobj(**kwargs)

    def private_name(self):
        return "__" + self.name


class ScalarAttribute(CustomIdlBase):
    def __init__(self, **kwargs):
        super(CustomIdlBase, self).__init__()
        self._init_xtextobj(**kwargs)

    def private_name(self):
        return "__"+self.name

class ArrayAttribute(CustomIdlBase):
    def __init__(self, **kwargs):
        super(CustomIdlBase, self).__init__()
        self._init_xtextobj(**kwargs)

    def private_name(self):
        return "__"+self.name

class FormulaBase(CustomIdlBase):
    def __init__(self):
        super(CustomIdlBase, self).__init__()

    def render_formula(self):
        raise Exception("base class - not implmented")

    def has_fixed_size(self):
        raise Exception("base class - not implmented")


class Sum(FormulaBase):
    def __init__(self, **kwargs):
        super(FormulaBase,self).__init__()
        self._init_xtextobj(**kwargs)

    def render_formula(self):
        return "+".join( map(lambda x:x.render_formula(), self.summands) )

    def has_fixed_size(self):
        return reduce(lambda x,y: x and y, map(lambda x: x.has_fixed_size(), self.summands), True)

class Mul(FormulaBase):
    def __init__(self, **kwargs):
        super(FormulaBase, self).__init__()
        self._init_xtextobj(**kwargs)

    def render_formula(self):
        return "*".join( map(lambda x:x.render_formula(), self.factors) )

    def has_fixed_size(self):
        return reduce(lambda x,y: x and y, map(lambda x: x.has_fixed_size(), self.factors), True)


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

    def has_fixed_size(self):
        if self.ref:
            return False
        elif self.sum:
            return self.sum.has_fixed_size()
        else:
            return True

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
                              classes=[Sum,Mul,Factor,ScalarRef,RawType,Struct,Attribute,ArrayAttribute,ScalarAttribute])

    mm.register_scope_provider({
        "*.*": scoping.ScopeProviderFullyQualifiedNamesWithImportURI(),
        "ScalarRef.ref0": scoping.ScopeProviderForSimpleRelativeNamedLookups("parent(Struct).attributes"),
        "ScalarRef.ref1": scoping.ScopeProviderForSimpleRelativeNamedLookups("ref0.type.attributes"),
        "ScalarRef.ref2": scoping.ScopeProviderForSimpleRelativeNamedLookups("ref1.type.attributes"),
    })
    return mm
