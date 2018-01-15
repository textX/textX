from custom_idl_metamodel import CustomIdlBase
from functools import reduce

class FormulaBase(CustomIdlBase):
    def __init__(self):
        super(FormulaBase, self).__init__()

    def render_formula(self,**p):
        raise Exception("base class - not implmented")

    def has_fixed_size(self):
        return reduce(lambda x,y: x and y, map(lambda x: x.has_fixed_size(), self.parts), True)

    def render_formula(self,**p):
        if len(self.parts)==1:
            return self.parts[0].render_formula(**p)
        else:
            return "("+self.operator.join( map(lambda x:x.render_formula(**p), self.parts) )+")"


class Sum(FormulaBase):
    def __init__(self, **kwargs):
        super(Sum,self).__init__()
        self._init_xtextobj(**kwargs)
        self.operator = "+"


class Dif(FormulaBase):
    def __init__(self, **kwargs):
        super(Dif, self).__init__()
        self._init_xtextobj(**kwargs)
        self.operator = "-"


class Mul(FormulaBase):
    def __init__(self, **kwargs):
        super(Mul, self).__init__()
        self._init_xtextobj(**kwargs)
        self.operator = "*"


class Div(FormulaBase):
    def __init__(self, **kwargs):
        super(Div, self).__init__()
        self._init_xtextobj(**kwargs)
        self.operator = "/"


class Val(FormulaBase):
    def __init__(self, **kwargs):
        super(Val, self).__init__()
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
        super(ScalarRef, self).__init__()
        self._init_xtextobj(**kwargs)

    def render_formula(self,separator=".",postfix="",prefix=""):
        return prefix+separator.join(map(lambda x: x.name,
                            filter(lambda x: x,
                                   [self.ref0, self.ref1, self.ref2])))+postfix
