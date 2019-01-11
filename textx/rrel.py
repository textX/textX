from __future__ import unicode_literals
from arpeggio import Optional, ZeroOrMore

# RREL grammar
def rrel_expression():      return rrel_path, ZeroOrMore(',', rrel_path)
def rrel_path():            return Optional('^'), rrel_subpath
def rrel_subpath():         return rrel_pathel, ZeroOrMore('.', rrel_pathel)
def rrel_pathel():          return [rrel_parent,
                                    rrel_plain_pathel,
                                    rrel_par_pathel], Optional('*')
def rrel_parent():
    from .lang import ident
    return 'parent', '(', ident, ')'
def rrel_plain_pathel():
    from .lang import ident
    return Optional('~'), ident
def rrel_par_pathel():      return '(', rrel_subpath, ')'


class RRELSublanguageVisitor(object):
    """
    This is a mixin class for a RREL sublanguage.
    It is used as one of the bases of `TextXVisitor`.
    """

    def visit_rrel_expression(self, node, children):
        pass

    def visit_rrel_path(self, node, children):
        pass

    def visit_rrel_subpath(self, node, children):
        pass

    def visit_rrel_pathel(self, node, children):
        pass

    def visit_rrel_parent(self, node, children):
        pass

    def visit_rrel_plain_pathel(self, node, children):
        pass

    def visit_rrel_par_pathel(self, node, children):
        pass
