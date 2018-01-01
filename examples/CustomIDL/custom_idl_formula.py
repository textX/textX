from custom_idl import CustomIdlBase
from functools import reduce

class FormulaBase(CustomIdlBase):
    def __init__(self):
        super(CustomIdlBase, self).__init__()

    def render_formula(self,**p):
        raise Exception("base class - not implmented")

    def has_fixed_size(self,**p):
        raise Exception("base class - not implmented")


class Sum(FormulaBase):
    def __init__(self, **kwargs):
        super(FormulaBase,self).__init__()
        self._init_xtextobj(**kwargs)

    def render_formula(self,**p):
        return "+".join( map(lambda x:x.render_formula(**p), self.summands) )

    def has_fixed_size(self):
        return reduce(lambda x,y: x and y, map(lambda x: x.has_fixed_size(), self.summands), True)

class Mul(FormulaBase):
    def __init__(self, **kwargs):
        super(FormulaBase, self).__init__()
        self._init_xtextobj(**kwargs)

    def render_formula(self,**p):
        return "*".join( map(lambda x:x.render_formula(**p), self.factors) )

    def has_fixed_size(self):
        return reduce(lambda x,y: x and y, map(lambda x: x.has_fixed_size(), self.factors), True)


class Factor(FormulaBase):
    def __init__(self, **kwargs):
        super(FormulaBase, self).__init__()
        self._init_xtextobj(**kwargs)

    def render_formula(self,**p):
        if self.ref:
            return self.ref.render_formula(**p)
        elif self.sum:
            return "({})".format(self.sum.render_formula(**p))
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

    def render_formula(self,separator=".",postfix=""):
        return separator.join(map(lambda x: x.name,
                            filter(lambda x: x,
                                   [self.ref0, self.ref1, self.ref2])))+postfix
