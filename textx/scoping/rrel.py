from arpeggio import EOF, Optional, PTNodeVisitor, visit_parse_tree
from arpeggio import RegExMatch as _
from arpeggio import ZeroOrMore as ArpeggioZeroOrMore


def rrel_id():
    return _(r"[^\d\W]\w*\b")  # from lang.py


def rrel_parent():
    return "parent", "(", rrel_id, ")"


def rrel_navigation():
    from textx.lang import string_value

    return [(Optional("~"), rrel_id), (Optional(string_value), "~", rrel_id)]


def rrel_brackets():
    return "(", rrel_sequence, ")"


def rrel_dots():
    return _(r"\.+")


def rrel_path_element():
    return [rrel_parent, rrel_brackets, rrel_navigation]


def rrel_zero_or_more():
    return rrel_path_element, "*"


def rrel_path():
    return [
        (
            Optional(["^", rrel_dots]),
            ArpeggioZeroOrMore([rrel_zero_or_more, rrel_path_element], "."),
            [rrel_zero_or_more, rrel_path_element],
        ),
        ["^", rrel_dots],
    ]


def rrel_sequence():
    return ArpeggioZeroOrMore(rrel_path, ","), rrel_path


def rrel_expression():
    return Optional(_(r"\+[mp]+:")), rrel_sequence


def rrel_standalone():
    return rrel_expression, EOF


class RRELBase:
    def __init__(self):
        pass

    def get_next_matches(
        self, obj, lookup_list, allowed, matched_path, first_element=False
    ):
        """
        This function yields potential matches encountered along the
        requested RREL.

        Implementation detail: This is the base implementation which
        assumes an apply function. Certain RREL classes overwrite this
        method instead of implementing the apply method.

        Args:
            obj: currently visited model object
            lookup_list: reference name to be looked up
            allowed: a callable to "allow" to visit an object
                in order to prevent infinite recursion loops.
                it is called with allowed(obj, lookup_list, RREL-entry).
            first_element: True, if we did not process any
                model element (else False). This is used to
                distinguish RRELs starting at model level (e.g.,
                'packages*.class') or locally (e.g., '.port').
        Returns (yields):
            yields (obj, lookup_list) to indicate possible
            intermediate matches. The returned obj can be
            Postponed.
        """
        if not allowed(obj, lookup_list, self):  # also adjusts visited objs
            return  # recursion stopper

        obj, lookup_list, matched_path = self.apply(
            obj, lookup_list, matched_path, first_element
        )
        if obj is None:
            return
        elif isinstance(obj, list):
            for iobj in obj:
                if iobj is not None:
                    yield iobj, lookup_list, matched_path
        else:
            yield obj, lookup_list, matched_path


class RRELParent(RRELBase):
    def __init__(self, type):
        super().__init__()
        self.type = type

    def __repr__(self):
        return f"parent({self.type})"

    def start_locally(self):
        return True

    def start_at_root(self):
        return False

    def apply(self, obj, lookup_list, matched_path, first_element):
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
                return obj, lookup_list, matched_path
        return None, lookup_list, matched_path


class RRELNavigation(RRELBase):
    def __init__(self, name, consume_name, fixed_name):
        super().__init__()
        self.name = name
        self.consume_name = consume_name
        self.fixed_name = fixed_name
        self.rrel_expression = None  # is set after tree is built, req. for +m flag

    def __repr__(self):
        if self.fixed_name is not None:
            assert not self.consume_name
            return "'" + self.fixed_name + "'~" + self.name
        else:
            return self.name if self.consume_name else "~" + self.name

    def start_locally(self):
        return False

    def start_at_root(self):
        return True

    def apply(self, obj, lookup_list, matched_path, first_element):
        """
        Args:
            obj: model object
            lookup_list: non-empty name list

        Returns:
            The object indicated by the navigation object,
            Postponed, None, or a list (if a list has to be processed).
        """
        assert self.rrel_expression is not None
        from textx.scoping import Postponed
        from textx.scoping.tools import needs_to_be_resolved

        if first_element:
            from textx import get_model

            obj = get_model(obj)

        start = [obj]
        # am I a root model node?
        if not hasattr(obj, "parent") and self.rrel_expression.importURI:
            if hasattr(obj, "_tx_model_repository"):
                for m in obj._tx_model_repository.local_models:
                    start.append(m)
            if obj._tx_metamodel.builtin_models:
                for m in obj._tx_metamodel.builtin_models:
                    start.append(m)

        if len(lookup_list) == 0 and self.consume_name:
            return None, lookup_list, matched_path

        def lookup(obj):
            if needs_to_be_resolved(obj, self.name):
                return Postponed(), lookup_list, matched_path
            if hasattr(obj, self.name):
                target = getattr(obj, self.name)
                if not self.consume_name and self.fixed_name is None:
                    return target, lookup_list, matched_path  # return list
                else:
                    if not isinstance(target, list):
                        target = [target]
                    if self.fixed_name is not None:
                        lst = list(
                            filter(
                                lambda x: hasattr(x, "name")
                                and x.name == self.fixed_name,
                                target,
                            )
                        )
                        if len(lst) > 0:
                            return (
                                lst[0],
                                lookup_list,
                                matched_path + [lst[0]],
                            )  # return obj
                        else:
                            return None, lookup_list, matched_path  # return None
                    else:
                        lst = list(
                            filter(
                                lambda x: hasattr(x, "name") and x.name == lookup_list[0],
                                target,
                            )
                        )
                        if len(lst) > 0:
                            return (
                                lst[0],
                                lookup_list[1:],
                                matched_path + [lst[0]],
                            )  # return obj
                        else:
                            return None, lookup_list, matched_path  # return None
            else:
                return None, lookup_list, matched_path

        for start_obj in start:
            res, res_lookup_list, res_lookup_path = lookup(start_obj)
            if res:
                return res, res_lookup_list, res_lookup_path

        return None, lookup_list, matched_path


class RRELBrackets(RRELBase):
    def __init__(self, oc):
        super().__init__()
        assert isinstance(oc, RRELSequence)
        self.seq = oc

    def start_locally(self):
        return self.seq.start_locally()

    def start_at_root(self):
        return self.seq.start_at_root()

    def __repr__(self):
        return "(" + str(self.seq) + ")"

    def get_next_matches(
        self, obj, lookup_list, allowed, matched_path, first_element=False
    ):
        if not allowed(obj, lookup_list, self):  # also adjusts visited objs
            return  # recursion stopper
        yield from self.seq.get_next_matches(
            obj, lookup_list, allowed, matched_path, first_element
        )


class RRELDots(RRELBase):
    def __init__(self, num):
        super().__init__()
        self.num = num

    def __repr__(self):
        return "." * self.num

    def start_locally(self):
        return True

    def start_at_root(self):
        return False

    def apply(self, obj, lookup_list, matched_path, first_element):
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
            return obj, lookup_list, matched_path
        else:
            return None, lookup_list, matched_path


class RRELSequence(RRELBase):
    def __init__(self, paths):
        super().__init__()
        self.paths = paths

    def __repr__(self):
        return ",".join(map(lambda x: str(x), self.paths))

    def start_locally(self):
        res = False
        for p in self.paths:
            res = res or p.start_locally()
        return res

    def start_at_root(self):
        res = False
        for p in self.paths:
            res = res or p.start_at_root()
        return res

    def get_next_matches(
        self, obj, lookup_list, allowed, matched_path, first_element=False
    ):
        if not allowed(obj, lookup_list, self):  # also adjusts visited objs
            return  # recursion stopper
        for ip in self.paths:
            yield from ip.get_next_matches(
                obj, lookup_list, allowed, matched_path, first_element
            )


class RRELZeroOrMore(RRELBase):
    def __init__(self, path_element):
        super().__init__()
        if not isinstance(path_element, RRELBrackets):
            path_element = RRELBrackets(RRELSequence([RRELPath([path_element])]))
        self.path_element = path_element
        assert isinstance(self.path_element, RRELBrackets)

    def start_locally(self):
        return self.path_element.start_locally()

    def start_at_root(self):
        return self.path_element.start_at_root()

    def __repr__(self):
        return str(self.path_element) + "*"

    def get_next_matches(
        self, obj, lookup_list, allowed, matched_path, first_element=False
    ):
        assert isinstance(self.path_element, RRELBrackets)
        from textx.scoping import Postponed

        def get_from_zero_or_more(obj, lookup_list, matched_path, first_element=False):
            assert self.start_locally() or self.start_at_root()  # or, not xor
            if not allowed(obj, lookup_list, self):  # also adjusts visited objs
                return  # recursion stopper
            if first_element:
                if self.start_locally():
                    yield obj, lookup_list, matched_path
                if self.start_at_root():
                    from textx import get_model

                    yield get_model(obj), lookup_list, matched_path
            else:
                yield obj, lookup_list, matched_path
            assert isinstance(self.path_element.seq, RRELSequence)
            for (
                iobj,
                ilookup_list,
                imatched_path,
            ) in self.path_element.seq.get_next_matches(
                obj, lookup_list, allowed, matched_path, first_element=first_element
            ):
                if isinstance(iobj, Postponed):
                    yield iobj, ilookup_list, imatched_path  # found postponed
                    return
                # yield from
                yield from get_from_zero_or_more(iobj, ilookup_list, imatched_path)

        prevent_doubles = set()
        for iobj, ilookup_list, imatched_path in get_from_zero_or_more(
            obj, lookup_list, matched_path, first_element
        ):
            if isinstance(iobj, Postponed):
                yield iobj, ilookup_list, imatched_path
                return
            if (id(iobj), len(ilookup_list)) not in prevent_doubles:
                prevent_doubles.add((id(iobj), len(ilookup_list)))
                yield iobj, ilookup_list, imatched_path


class RRELPath(RRELBase):
    def __init__(self, path_elements):
        super().__init__()
        # print("create Path :" + str(path_elements))
        self.path_elements = path_elements
        if self.path_elements[0] == "^":
            self.path_elements[0] = RRELZeroOrMore(
                RRELBrackets(RRELSequence([RRELPath([RRELDots(2)])]))
            )

    def __repr__(self):
        if isinstance(self.path_elements[0], RRELDots):
            return str(self.path_elements[0]) + ".".join(
                map(lambda x: str(x), self.path_elements[1:])
            )
        else:
            return ".".join(map(lambda x: str(x), self.path_elements))

    def start_locally(self):
        return self.path_elements[0].start_locally()

    def start_at_root(self):
        return self.path_elements[0].start_at_root()

    def get_next_matches(
        self, obj, lookup_list, allowed, matched_path, first_element=False
    ):
        from textx.scoping import Postponed

        def intern_get_next_matches(
            obj, lookup_list, allowed, matched_path, first_element=False, idx=0
        ):
            assert len(self.path_elements) > idx
            e = self.path_elements[idx]
            for iobj, ilookup_list, imatched_path in e.get_next_matches(
                obj, lookup_list, allowed, matched_path, first_element
            ):
                if isinstance(iobj, Postponed):
                    yield iobj, ilookup_list, imatched_path
                    return
                if len(self.path_elements) - 1 == idx:
                    yield iobj, ilookup_list, imatched_path
                else:
                    yield from intern_get_next_matches(
                        iobj,
                        ilookup_list,
                        allowed,
                        imatched_path,
                        first_element=False,
                        idx=idx + 1,
                    )

        yield from intern_get_next_matches(
            obj, lookup_list, allowed, matched_path, first_element, 0
        )


class RRELExpression:
    def __init__(self, seq, flags):
        self.seq = seq
        self.flags = flags
        self.importURI = "m" in flags
        self.use_proxy = "p" in flags

        def prepare_tree(node):
            if isinstance(node, RRELNavigation):
                node.rrel_expression = self
            if isinstance(node, RRELBase):
                for c in node.__dict__.values():
                    if isinstance(c, list):
                        for e in c:
                            prepare_tree(e)
                    else:
                        prepare_tree(c)

        prepare_tree(self.seq)

    def __repr__(self):
        if self.importURI:
            return "+" + self.flags + ":" + str(self.seq)
        else:
            return str(self.seq)


class RRELVisitor(PTNodeVisitor):
    def visit_rrel_parent(self, node, children):
        return RRELParent(children[0])

    def visit_rrel_navigation(self, node, children):
        if len(children) == 2:
            if "string_value" in children.results:
                return RRELNavigation(children[1], False, children[0])
            else:
                return RRELNavigation(children[1], False, None)
        else:
            return RRELNavigation(children[0], True, None)

    def visit_rrel_brackets(self, node, children):
        assert len(children) == 1  # a path
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
        assert len(children) == 1
        return children[0]

    def visit_rrel_expression(self, node, children):
        if len(children) == 1:
            return RRELExpression(children[0], "")
        else:
            flags = children[0][1:-1]  # see grammar
            return RRELExpression(children[1], flags)

    def visit_string_value(self, node, children):
        return node.value[1:-1]


class ReferenceProxy:
    """
    This class describes a resolved reference of an RREL
    with 'p'-flag set ('+p:'). It can be used similar to
    a normally resolved reference concerning the following
    semantics: getattr, setattr, delattr and '=='.

    With this, a ReferenceProxy object is compatible with the
    `textx.textx_isinstance` semantics.

    It further provides
     - an attribute '_tx_obj', corresponding
       exactly to the resolved reference.
     - an attribute '_tx_path', a list of objects
       describing the path of named objects traversed
       during reference resolution.
    """

    def __init__(self, path):
        assert len(path) > 0
        self.__dict__["_tx_path"] = path

    def __setattr__(self, key, value):
        if key == "_tx_path" or key == "_tx_obj":
            raise Exception("not allowed to set _tx_path or _tx_obj")
        return setattr(self.__dict__["_tx_path"][-1], key, value)

    def __getattr__(self, item):
        if item == "_tx_path":
            return self.__dict__["_tx_path"]
        elif item == "_tx_obj":
            return self.__dict__["_tx_path"][-1]
        else:
            return getattr(self.__dict__["_tx_path"][-1], item)

    def __delattr__(self, item):
        if item == "_tx_path" or item == "_tx_obj":
            raise Exception("not allowed to del _tx_path or _tx_obj")
        return delattr(self.__dict__["_tx_path"][-1], item)

    def __eq__(self, other):
        return self.__dict__["_tx_path"][-1] == other


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


def find_object_with_path(obj, lookup_list, rrel_tree, obj_cls=None, split_string="."):
    from textx import textx_isinstance
    from textx.scoping import Postponed

    if isinstance(rrel_tree, str):
        rrel_tree = parse(rrel_tree)
    assert isinstance(rrel_tree, RRELExpression)
    rrel_tree = rrel_tree.seq
    assert isinstance(rrel_tree, RRELSequence)
    if isinstance(lookup_list, str):
        lookup_list = lookup_list.split(split_string)
        lookup_list = list(filter(lambda x: len(x) > 0, lookup_list))
    visited = [set() for _ in range(len(lookup_list) + 1)]

    def allowed(obj, lookup_list, e):
        if (id(obj), id(e)) in visited[len(lookup_list)]:
            return False
        else:
            visited[len(lookup_list)].add((id(obj), id(e)))
            return True

    for p in rrel_tree.paths:
        for obj_res, lookup_list_res, matched_path in p.get_next_matches(
            obj, lookup_list, allowed, [], first_element=True
        ):
            if isinstance(obj_res, Postponed):
                return obj_res  # Postponed
            elif len(lookup_list_res) == 0 and (
                obj_cls is None or textx_isinstance(obj_res, obj_cls)
            ):
                return obj_res, matched_path  # found match
    return None  # not found


def find(obj, lookup_list, rrel_tree, obj_cls=None, split_string=".", use_proxy=False):
    """
    This function gets all/one element from a model
    object based on an rrel tree (query).

    Args:
        obj: model object (starting point of the search)
        lookup_list: list of name parts forming the full name.
        rrel_tree: the query (must be a RRELExpression object or a string)
        split_string: the string used to split the name into individual
            parts (e.g. '.' for a python-like name schema or '::' for a
            C++-like name schema for namespace resolution)
        use_proxy: return a path proxy object (see ReferenceProxy) instead
            of the normal result of the query.

    Returns:
        The result of the query (first match), a
        Postponed object, or None (nothing found)
    """
    res = find_object_with_path(obj, lookup_list, rrel_tree, obj_cls, split_string)
    if type(res) is tuple:
        # full path is in res[1]
        if use_proxy:
            return ReferenceProxy(res[1])
        else:
            return res[0]
    else:
        return res


def create_rrel_scope_provider(rrel_tree_or_string, split_string=None, **kwargs):
    """
    This function creates a RREL scope provider.

    Args:
        rrel_tree_or_string: the query (see `rrel.find`)
        split_string: the string used to split the name into individual
            parts (see `rrel.find`). It it is None, the match
            rule associated with a reference is used to deduce the
            delimiter (parameter `split`). Else `.` is used.

    Returns:
        The result of the query (first match), a
        Postponed object, or None (nothing found)
    """
    from textx.scoping.providers import ImportURI

    class RREL:
        """
        RREL scope provider
        """

        def __init__(self, rrel_tree, split_string, use_proxy):
            """
            Creates a RREL scope provider

            Args:
                rrel_tree: the query (see `rrel.find`)
                split_string: the string used to split the name into individual
                    parts (see `create_rrel_scope_provider`)
                use_proxy: see find
            """
            self.rrel_tree = rrel_tree
            self.split_string = split_string
            self.use_proxy = use_proxy

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

            if self.split_string is None:
                from textx import get_metamodel

                rule = get_metamodel(current_obj)[obj_ref.match_rule_name]
                if hasattr(rule._tx_peg_rule, "split"):
                    split = rule._tx_peg_rule.split
                else:
                    split = "."
            else:
                split = self.split_string

            return find(
                current_obj,
                obj_name,
                self.rrel_tree,
                obj_cls,
                split_string=split,
                use_proxy=self.use_proxy,
            )

    class RRELImportURI(ImportURI):
        """
        scope provider with ImportURI and RREL
        """

        def __init__(
            self,
            rrel_tree,
            split_string,
            use_proxy,
            glob_args=None,
            search_path=None,
            importAs=False,
            importURI_converter=None,
            importURI_to_scope_name=None,
        ):
            ImportURI.__init__(
                self,
                RREL(rrel_tree, split_string, use_proxy),
                glob_args=glob_args,
                search_path=search_path,
                importAs=importAs,
                importURI_converter=importURI_converter,
                importURI_to_scope_name=importURI_to_scope_name,
            )

        def __call__(self, obj, attr, obj_ref):
            # override `__call__`in order to ignore the `default ImportURI`
            # implementation: Here, we just need to call the normal
            # scope resolution of the RREL provider (+the `ModelLoader`
            # feature of the `ImportURI` implementation):
            return self.scope_provider(obj, attr, obj_ref)

    if isinstance(rrel_tree_or_string, str):
        rrel_tree_or_string = parse(rrel_tree_or_string)

    if rrel_tree_or_string.importURI:
        return RRELImportURI(
            rrel_tree_or_string, split_string, rrel_tree_or_string.use_proxy, *kwargs
        )
    else:
        return RREL(rrel_tree_or_string, split_string, rrel_tree_or_string.use_proxy)
