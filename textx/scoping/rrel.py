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
    return '(', ordered_choice, ')'


def dots():
    return _(r'\.+')


def path_element():
    return [parent, brackets, navigation]


def zero_or_more():
    return path_element, '*'


def path():
    return Optional(['^', dots]), ArpeggioZeroOrMore(
        [zero_or_more, path_element], '.'), Optional([zero_or_more, path_element])


def ordered_choice():
    return ArpeggioZeroOrMore(path, ","), path


def rrel():
    return ordered_choice, EOF


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
        if len(lookup_list) == 0 and self.consume_name:
            return None, lookup_list
        if needs_to_be_resolved(obj, self.name):
            return Postponed(), lookup_list
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
    def __init__(self, oc):
        assert isinstance(oc, OrderedChoice)
        self.oc = oc

    def __repr__(self):
        return '(' + str(self.oc) + ')'


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


class OrderedChoice:
    def __init__(self, paths):
        self.paths = paths

    def __repr__(self):
        return ','.join(map(lambda x: str(x), self.paths))


class ZeroOrMore:
    def __init__(self, path_element):
        if not isinstance(path_element, Brackets):
            path_element = Brackets(OrderedChoice([Path([path_element])]))
        self.path_element = path_element
        assert(isinstance(self.path_element, Brackets))

    def __repr__(self):
        return str(self.path_element) + '*'


class Path:
    def __init__(self, path_elements):
        # print("create Path :" + str(path_elements))
        self.path_elements = path_elements
        if (self.path_elements[0] == '^'):
            self.path_elements[0] = ZeroOrMore(Brackets(OrderedChoice([Path([Dots(2)])])))

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

    def visit_ordered_choice(self, node, children):
        return OrderedChoice(children)

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


def find(obj, lookup_list, rrel_tree, obj_cls=None):
    """
    This function gets all/one element from a model
    object based on an rrel tree (query).

    Note: this function uses Python 3.3+ features (recursive generators)

    Args:
        obj: model object (starting point of the search)
        lookup_list: list of name parts forming the full name.
        rrel_tree: the query (must be a Path object)

    Returns:
        The result of the query (first match), a
        Postponed object, or None (nothing found)
    """
    if isinstance(rrel_tree, str):
        rrel_tree = parse(rrel_tree)
    if isinstance(lookup_list, str):
        lookup_list = lookup_list.split(".")
        lookup_list = list(filter(lambda x: len(x) > 0, lookup_list))
    visited = [set()] * (len(lookup_list) + 1)

    def get_next_matches(obj, lookup_list, p, idx=0):
        # print("get_next_matches: ",obj, lookup_list, idx)
        assert isinstance(p, Path)
        assert len(p.path_elements) >= idx
        # assert len(lookup_list) > 0
        for e in p.path_elements[idx:]:
            if hasattr(e, "apply"):
                obj, lookup_list = e.apply(obj, lookup_list)
                if obj is not None and isinstance(obj, Postponed):
                    yield obj, lookup_list
                    return
                if obj is None:
                    return
                elif isinstance(obj, list):
                    for iobj in obj:
                        yield from get_next_matches(iobj, lookup_list, p, idx + 1)
                    return
            elif isinstance(e, Brackets):
                for ip in e.oc.paths:
                    for iobj, ilookup_list in get_next_matches(obj, lookup_list, ip):
                        yield from get_next_matches(iobj, ilookup_list, p, idx + 1)
                return
            elif isinstance(e, ZeroOrMore):
                assert isinstance(e.path_element, Brackets)
                def get_from_zero_or_more(obj, lookup_list):
                    yield obj, lookup_list
                    assert isinstance(e.path_element, Brackets)
                    assert isinstance(e.path_element.oc, OrderedChoice)
                    for ip in e.path_element.oc.paths:
                        for iobj, ilookup_list in get_next_matches(obj, lookup_list, ip):
                            # print(ip, iobj, ilookup_list)
                            if (iobj, ip) in visited[len(ilookup_list)]:
                                continue
                            if iobj is not None and isinstance(iobj, Postponed):
                                yield iobj, ilookup_list  # found postponed
                                return
                            visited[len(ilookup_list)].add((iobj, ip))
                            yield from get_from_zero_or_more(iobj, ilookup_list)

                prevent_doubles = set()
                for obj, lookup_list in get_from_zero_or_more(obj, lookup_list):
                    if (obj, len(lookup_list)) not in prevent_doubles:
                        yield from get_next_matches(obj, lookup_list, p, idx + 1)
                        prevent_doubles.add((obj, len(lookup_list)))
                return
            idx += 1
        yield obj, lookup_list

    for p in rrel_tree.paths:
        for obj_res, lookup_list_res in get_next_matches(obj, lookup_list, p):
            if isinstance(obj_res, Postponed):
                return obj_res  # Postponed
            elif len(lookup_list_res) == 0:
                print("MATCH?", obj_res)
                if obj_cls is None or textx_isinstance(obj_res, obj_cls):
                    return obj_res  # found match
    return None  # not found


class RREL(object):
    """
    RREL scope provider
    """
    def __init__(self, rrel_tree):
        if isinstance(rrel_tree, str):
            rrel_tree = parse(rrel_tree)
        self.rrel_tree = rrel_tree

    def __call__(self, current_obj, attr, obj_ref):
        """
        find an object

        Args:
            current_obj: object corresponding a instance of an
                         object (rule instance)
            attr: the referencing attribute (unused)
            obj_ref: ObjCrossRef to be resolved

        Returns: None or the referenced object
        """
        obj_cls, obj_name = obj_ref.cls, obj_ref.obj_name
        lookup_list = obj_name.split(".")
        lookup_list = list(filter(lambda x: len(x) > 0, lookup_list))

        return find(current_obj, lookup_list, self.rrel_tree, obj_cls)
