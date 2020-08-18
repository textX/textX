from arpeggio import PTNodeVisitor, visit_parse_tree
from arpeggio import Optional, EOF
from arpeggio import ZeroOrMore as ArpeggioZeroOrMore
from arpeggio import RegExMatch as _


def rrel_id():
    return _(r'[^\d\W]\w*\b')  # from lang.py


def rrel_parent():
    return 'parent', '(', rrel_id, ')'


def rrel_navigation():
    return Optional('~'), rrel_id


def rrel_brackets():
    return '(', rrel_sequence, ')'


def rrel_dots():
    return _(r'\.+')


def rrel_path_element():
    return [rrel_parent, rrel_brackets, rrel_navigation]


def rrel_zero_or_more():
    return rrel_path_element, '*'


def rrel_path():
    return Optional(['^', rrel_dots]), ArpeggioZeroOrMore(
        [rrel_zero_or_more, rrel_path_element], '.'),\
           Optional([rrel_zero_or_more, rrel_path_element])


def rrel_sequence():
    return ArpeggioZeroOrMore(rrel_path, ","), rrel_path


def rrel_standalone():
    return rrel_sequence, EOF


class RRELParent:
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
        from textx import get_metamodel, textx_isinstance
        t = get_metamodel(obj)[self.type]
        while hasattr(obj, "parent"):
            obj = obj.parent
            if textx_isinstance(obj, t):
                return obj, lookup_list
        return None, lookup_list


class RRELNavigation:
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
        from textx.scoping.tools import needs_to_be_resolved
        from textx.scoping import Postponed
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


class RRELBrackets:
    def __init__(self, oc):
        assert isinstance(oc, RRELSequence)
        self.oc = oc

    def __repr__(self):
        return '(' + str(self.oc) + ')'


class RRELDots:
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


class RRELSequence:
    def __init__(self, paths):
        self.paths = paths

    def __repr__(self):
        return ','.join(map(lambda x: str(x), self.paths))


class RRELZeroOrMore:
    def __init__(self, path_element):
        if not isinstance(path_element, RRELBrackets):
            path_element = RRELBrackets(RRELSequence(
                [RRELPath([path_element])]))
        self.path_element = path_element
        assert(isinstance(self.path_element, RRELBrackets))

    def __repr__(self):
        return str(self.path_element) + '*'


class RRELPath:
    def __init__(self, path_elements):
        # print("create Path :" + str(path_elements))
        self.path_elements = path_elements
        if (self.path_elements[0] == '^'):
            self.path_elements[0] = RRELZeroOrMore(RRELBrackets(
                RRELSequence([RRELPath([RRELDots(2)])])))

    def __repr__(self):
        if isinstance(self.path_elements[0], RRELDots):
            return str(self.path_elements[0]) + '.'.join(
                map(lambda x: str(x), self.path_elements[1:]))
        else:
            return '.'.join(map(lambda x: str(x), self.path_elements))


class RRELVisitor(PTNodeVisitor):

    def visit_rrel_parent(self, node, children):
        return RRELParent(children[0])

    def visit_rrel_navigation(self, node, children):
        if len(children) == 1:
            return RRELNavigation(children[0], True)
        else:
            return RRELNavigation(children[1], False)

    def visit_rrel_brackets(self, node, children):
        assert(len(children) == 1)  # a path
        return RRELBrackets(children[0])

    def visit_rrel_dots(self, node, children):
        return RRELDots(len(node.value))

    def visit_rrel_zero_or_more(self, node, children):
        return RRELZeroOrMore(children[0])

    def visit_rrel_path(self, node, children):
        return RRELPath(children)

    def visit_rrel_sequence(self, node, children):
        return RRELSequence(children)

    def visit_rrel_path_element(self, node, children):
        assert(len(children) == 1)
        return children[0]


def parse(rrel_expression):
    """
    This function parses a rrel path and returns a RREL expression tree.

    Args:
        rrel_expression: the RREL expression (string).

    Returns:
        A RREL expression tree.
    """
    from arpeggio import ParserPython
    parser = ParserPython(rrel_standalone, reduce_tree=False)
    parse_tree = parser.parse(rrel_expression)
    return visit_parse_tree(parse_tree, RRELVisitor())


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
    from textx import textx_isinstance
    from textx.scoping import Postponed
    if isinstance(rrel_tree, str):
        rrel_tree = parse(rrel_tree)
    if isinstance(lookup_list, str):
        lookup_list = lookup_list.split(".")
        lookup_list = list(filter(lambda x: len(x) > 0, lookup_list))
    visited = [set()] * (len(lookup_list) + 1)

    def get_next_matches(obj, lookup_list, p, idx=0):
        # print("get_next_matches: ",obj, lookup_list, idx)
        assert isinstance(p, RRELPath)
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
            elif isinstance(e, RRELBrackets):
                for ip in e.oc.paths:
                    for iobj, ilookup_list in get_next_matches(obj, lookup_list, ip):
                        yield from get_next_matches(iobj, ilookup_list, p, idx + 1)
                return
            elif isinstance(e, RRELZeroOrMore):
                assert isinstance(e.path_element, RRELBrackets)

                def get_from_zero_or_more(obj, lookup_list):
                    yield obj, lookup_list
                    assert isinstance(e.path_element, RRELBrackets)
                    assert isinstance(e.path_element.oc, RRELSequence)
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
