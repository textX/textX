from arpeggio import Optional, EOF
from arpeggio import ZeroOrMore as ArpeggioZeroOrMore
from arpeggio import RegExMatch as _
from arpeggio import PTNodeVisitor, visit_parse_tree

def id():
    return _(r'[^\d\W]\w*\b')  # from lang.py


def parent():
    return 'parent', '(', id, ')'


def navigation():
    return Optional('~'), id


def brackets():
    return '(', path, ')'


def dots():
    return _(r'\.+')


def path_element():
    return [parent, brackets, navigation]


def zero_or_more():
    return path_element, '*'


def path():
    return Optional(['^', dots]), ArpeggioZeroOrMore(
        [zero_or_more, path_element], '.'), [
        zero_or_more, path_element]


def rrel():
    return path, EOF


class Parent:
    def __init__(self, type):
        self.type = type

    def __repr__(self):
        return 'parent({})'.format(self.type)


class Navigation:
    def __init__(self, name, consume_name=True):
        self.name = name
        self.consume_name = consume_name

    def __repr__(self):
        return '~'+self.name if self.consume_name else self.name


class Brackets:
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return '('+str(path)+')'


class Dots:
    def __init__(self, num):
        self.num = num

    def __repr__(self):
        return '('+('.'*self.num)+')'


class ZeroOrMore:
    def __init__(self, path_element):
        self.path_element = path_element

    def __repr__(self):
        return str(self.path_element)+'*'


class Path:
    def __init__(self, path_elements):
        self.path_elements = path_elements

    def __repr__(self):
        return '.'.join(map(lambda x:str(x), self.path_elements))


class RrelVisitor(PTNodeVisitor):

    def visit_parent(self, node, children):
        return Parent(node.value)  # TODO

    def visit_navigaton(self, node, children):
        return Navigation(node.value)  # TODO

    def visit_brackets(self, node, children):
        return Brackets(children)  # TODO

    def visit_dots(self, node, children):
        return Dots(len(node.value))  # TODO

    def visit_zero_or_more(self, node, children):
        return ZeroOrMore(node.value)  # TODO

    def visit_path(self, node, children):
        return Path(children)  # TODO


def parse(rrel_expression):
    from arpeggio import ParserPython
    parser = ParserPython(rrel)
    parse_tree = parser.parse(rrel_expression)
    return visit_parse_tree(parse_tree, RrelVisitor())

