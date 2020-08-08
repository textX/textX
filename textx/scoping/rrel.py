from textx import get_metamodel, textx_isinstance
from textx.scoping.tools import needs_to_be_resolved
from textx.scoping import Postponed
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

    def apply(self, obj, lookup_list):
        """
        Args:
            obj: model object
            lookup_list: non-empty name list (not used)

        Returns:
            The parent of the specified type or None.
        """
        t = get_metamodel(obj)[self.type]
        while hasattr(obj, "parent"):
            obj = obj.parent
            if textx_isinstance(obj, t):
                return obj, lookup_list
        return None, lookup_list


class Navigation:
    def __init__(self, name, consume_name):
        self.name = name
        self.consume_name = consume_name

    def __repr__(self):
        return self.name if self.consume_name else '~' + self.name

    def apply(self, obj, lookup_list):
        """
        Args:
            obj: model object
            lookup_list: non-empty name list

        Returns:
            The object indicated by the navigation object,
            Postponed, None, or a list (if a list has to be processed).
        """
        if needs_to_be_resolved(obj, self.name):
            return Postponed()
        if hasattr(obj, self.name):
            target = getattr(obj, self.name)
            if isinstance(target, list):
                if not self.consume_name:
                    return target, lookup_list  # return list
                else:
                    lst = list(filter(lambda x: hasattr(
                        x, "name") and getattr(
                        x, "name") == lookup_list[0], target))
                    if len(lst) > 0:
                        return lst[0], lookup_list[1:]  # return obj
                    else:
                        return None, lookup_list  # return None
            else:
                if not self.consume_name:
                    return target, lookup_list
                else:
                    if hasattr(target, "name") and getattr(
                            target, "name") == lookup_list[0]:
                        return target, lookup_list[1:]  # return obj
                    else:
                        return None, lookup_list  # return None
        else:
            return None, lookup_list


class Brackets:
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return '(' + str(self.path) + ')'


class Dots:
    def __init__(self, num):
        self.num = num

    def __repr__(self):
        return ('.' * self.num)

    def apply(self, obj, lookup_list):
        """
        Args:
            obj: model object
            lookup_list: non-empty name list (not used)

        Returns:
            The parent or None.
        """
        num = self.num
        while num > 1 and hasattr(obj, "parent"):
            obj = obj.parent
            num -= 1
        if num <= 1:
            return obj, lookup_list
        else:
            return None, lookup_list


class ZeroOrMore:
    def __init__(self, path_element):
        if not isinstance(path_element, Brackets):
            path_element = Brackets(Path([path_element]))
        self.path_element = path_element
        assert(isinstance(self.path_element, Brackets))

    def __repr__(self):
        return str(self.path_element) + '*'


class Path:
    def __init__(self, path_elements):
        # print("create Path :" + str(path_elements))
        self.path_elements = path_elements
        if (self.path_elements[0] == '^'):
            self.path_elements[0] = ZeroOrMore(Brackets(Path([Dots(2)])))

    def __repr__(self):
        if isinstance(self.path_elements[0], Dots):
            return str(self.path_elements[0]) + '.'.join(
                map(lambda x: str(x), self.path_elements[1:]))
        else:
            return '.'.join(map(lambda x: str(x), self.path_elements))


class RrelVisitor(PTNodeVisitor):

    def visit_parent(self, node, children):
        return Parent(children[0])

    def visit_navigation(self, node, children):
        if len(children) == 1:
            return Navigation(children[0], True)
        else:
            return Navigation(children[1], False)

    def visit_brackets(self, node, children):
        assert(len(children) == 1)  # a path
        return Brackets(children[0])

    def visit_dots(self, node, children):
        return Dots(len(node.value))

    def visit_zero_or_more(self, node, children):
        return ZeroOrMore(children[0])

    def visit_path(self, node, children):
        return Path(children)

    def visit_path_element(self, node, children):
        assert(len(children) == 1)
        return children[0]


def parse(rrel_expression):
    """
    This function parses a rrel path and returns a RREL expression tree.

    Args:
        rrel_expression: the RREL expression.

    Returns:
        A RREL expression tree.
    """
    from arpeggio import ParserPython
    parser = ParserPython(rrel, reduce_tree=False)
    parse_tree = parser.parse(rrel_expression)
    return visit_parse_tree(parse_tree, RrelVisitor())


def find(obj, lookup_list, rrel_tree):
    """
    This function gets all/one element from a model
    object based on an rrel tree (query).

    Args:
        obj: model object (starting point of the search)
        lookup_list: list of name parts forming the full name.
        rrel_tree: the query (must be a Path oebjct)

    Returns:
        The result of the query (first match), a
        Postponed object, or None (nothing found)
    """
    if isinstance(rrel_tree, str):
        rrel_tree = parse(rrel_tree)
    if isinstance(lookup_list, str):
        lookup_list = lookup_list.split(".")

    def apply(obj, lookup_list, p, idx=0):
        assert isinstance(p, Path)
        assert len(p.path_elements) >= idx
        # assert len(lookup_list) > 0
        for e in p.path_elements[idx:]:
            if hasattr(e, "apply"):
                obj, lookup_list = e.apply(obj, lookup_list)
                if isinstance(obj, Postponed):
                    return obj, lookup_list
            elif isinstance(e, Brackets):
                obj, lookup_list = apply(obj, lookup_list, e.path)
                if isinstance(obj, Postponed):
                    return obj, lookup_list
            elif isinstance(e, ZeroOrMore):
                obj_temp = obj
                lookup_list_temp = lookup_list
                visited = set()
                while obj_temp is not None and len(lookup_list_temp) > 0:
                    obj_res, lookup_list_res = apply(obj_temp, lookup_list_temp, p, idx+1)
                    if obj_res is not None and (
                            isinstance(obj_res, Postponed) or len(lookup_list_res)==0):
                        return obj_res, lookup_list_res  # found match / postponed
                    obj_temp, lookup_list_temp = apply(
                        obj_temp, lookup_list_temp, e.path_element.path)
                    if obj_temp in visited:
                        break
                    if obj_temp is not None and (
                            isinstance(obj_temp, Postponed) or len(lookup_list_res)==0):
                        return obj_temp, lookup_list_temp  # found match / postponed
                    visited.add(obj_temp)
                return obj_temp, lookup_list_temp
            idx += 1
        return obj, lookup_list

    obj_res, lookup_list_res = apply(obj, lookup_list, rrel_tree)
    if isinstance(obj_res, Postponed):
        return obj_res  # Postponed
    elif obj_res is not None and len(lookup_list_res) == 0:
        return obj_res  # found match
    else:
        return None  # not found
