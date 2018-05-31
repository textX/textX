#######################################################################
# Name: model.py
# Purpose: Model construction.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright:
#    (c) 2014-2017 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

import sys
import codecs
import traceback
from collections import OrderedDict
from arpeggio import Parser, Sequence, NoMatch, EOF, Terminal
from textx.exceptions import TextXSyntaxError, TextXSemanticError
from textx.const import MULT_OPTIONAL, MULT_ONE, MULT_ONEORMORE, \
    MULT_ZEROORMORE, RULE_ABSTRACT, RULE_MATCH, MULT_ASSIGN_ERROR, \
    UNKNOWN_OBJ_ERROR
from textx.lang import PRIMITIVE_PYTHON_TYPES
from textx.scoping import Postponed
from textx.scoping.providers import PlainName as DefaultScopeProvider

if sys.version < '3':
    text = unicode  # noqa
else:
    text = str

__all__ = ['get_children_of_type', 'get_parent_of_type', 'get_model',
           'get_metamodel']


def get_model(obj):
    """
    Finds model root element for the given object.
    """
    p = obj
    while hasattr(p, 'parent'):
        p = p.parent
    return p


def get_metamodel(obj):
    """
    Returns metamodel of the given object's model.
    """
    return get_model(obj)._tx_metamodel


def get_parent_of_type(typ, obj):
    """
    Finds first object up the parent chain of the given type.
    If no parent of the given type exists None is returned.

    Args:
        typ(str or python class): The type of the model object we are
            looking for.
        obj (model object): Python model object which is the start of the
            search process.
    """
    if type(typ) is not text:
        typ = typ.__name__

    while hasattr(obj, 'parent'):
        obj = obj.parent
        if obj.__class__.__name__ == typ:
            return obj


def get_children(decider, root):
    """
    Returns a list of all model elements of type 'typ' starting from model
    element 'root'. The search process will follow containment links only.
    Non-containing references shall not be followed.

    Args:
        decider(obj): a callable returning True if the object is of interest.
        root (model object): Python model object which is the start of the
            search process.
    """
    collected = []

    def follow(elem):

        if elem in collected:
            return

        # Use meta-model to search for all contained child elements.
        cls = elem.__class__

        if hasattr(cls, '_tx_attrs') and decider(elem):
            collected.append(elem)

        if hasattr(cls, '_tx_attrs'):
            for attr_name, attr in cls._tx_attrs.items():
                # Follow only attributes with containment semantics
                if attr.cont:
                    if attr.mult in (MULT_ONE, MULT_OPTIONAL):
                        new_elem = getattr(elem, attr_name)
                        if new_elem:
                            follow(new_elem)
                    else:
                        new_elem_list = getattr(elem, attr_name)
                        if new_elem_list:
                            for new_elem in new_elem_list:
                                follow(new_elem)

    follow(root)
    return collected


def get_children_of_type(typ, root):
    """
    Returns a list of all model elements of type 'typ' starting from model
    element 'root'. The search process will follow containment links only.
    Non-containing references shall not be followed.

    Args:
        typ(str or python class): The type of the model object we are
            looking for.
        root (model object): Python model object which is the start of the
            search process.
    """

    if type(typ) is not text:
        typ = typ.__name__

    return get_children(lambda x: x.__class__.__name__ == typ, root)


def convert(value, _type):
    """
    Convert instances of textx types to python types.
    """
    return {
            'BOOL': lambda x: x == '1' or x.lower() == 'true',
            'INT': lambda x: int(x),
            'FLOAT': lambda x: float(x),
            'STRING': lambda x: x[1:-1].replace(r'\"',
                                                r'"').replace(r"\'", "'"),
            }.get(_type, lambda x: x)(value)


class ObjCrossRef(object):
    """
    Used for object cross reference resolving.

    Attributes:
        obj_name(str): A name of the target object.
        cls(TextXClass): The target object class.
        position(int): A position in the input string of this cross-ref.
    """

    def __init__(self, obj_name, cls, position):
        self.obj_name = obj_name
        self.cls = cls
        self.position = position


class RefRulePosition(object):
    """
    Used for "go to definition" support in textx-languageserver

    Attributes:
        name(str): A name of the target object.
        ref_pos_start(int): Reference starting position
        ref_pos_end(int): Reference ending position
        def_pos_start(int): Starting position of referenced object
        def_pos_end(int): Ending position of referenced object
    """

    def __init__(self, name, ref_pos_start, ref_pos_end,
                 def_pos_start, def_pos_end):
        self.name = name
        self.ref_pos_start = ref_pos_start
        self.ref_pos_end = ref_pos_end
        self.def_pos_start = def_pos_start
        self.def_pos_end = def_pos_end


def get_model_parser(top_rule, comments_model, **kwargs):
    """
    Creates model parser for the given language.
    """

    class TextXModelParser(Parser):
        """
        Parser created from textual textX language description.
        Semantic actions for this parser will construct object
        graph representing model on the given language.
        """

        def __init__(self, *args, **kwargs):
            super(TextXModelParser, self).__init__(*args, **kwargs)

            # By default first rule is starting rule
            # and must be followed by the EOF
            self.parser_model = Sequence(
                nodes=[top_rule, EOF()], rule_name='Model', root=True)
            self.comments_model = comments_model

            # Stack for metaclass instances
            self._inst_stack = []

            # Dict for cross-ref resolving
            # { id(class): { obj.name: obj}}
            self._instances = {}

            # List to keep track of all cross-ref that need to be resolved
            # Contained elements are tuples: (instance, metaattr, cross-ref)
            self._crossrefs = []

        def clone(self):
            """
            Responsibility: create a clone in order to parse a separate file.
            It must Kbe possible that more than one clone exist in parallel,
            without being influenced by other parser clones.

            Returns:
                A clone of this parser
            """
            import copy
            the_clone = copy.copy(self)  # shallow copy

            # create new objects for parse-dependent data
            the_clone._inst_stack = []
            the_clone._instances = {}
            the_clone._crossrefs = []

            # TODO self.memoization = memoization
            the_clone.comments = []
            the_clone.comment_positions = {}
            the_clone.sem_actions = {}

            return the_clone

        def _parse(self):
            try:
                return self.parser_model.parse(self)
            except NoMatch as e:
                line, col = e.parser.pos_to_linecol(e.position)
                raise TextXSyntaxError(message=text(e),
                                       line=line,
                                       col=col,
                                       expected_rules=e.rules)

        def get_model_from_file(self, file_name, encoding, debug,
                                pre_ref_resolution_callback=None,
                                is_main_model=True):
            """
            Creates model from the parse tree from the previous parse call.
            If file_name is given file will be parsed before model
            construction.
            """
            with codecs.open(file_name, 'r', encoding) as f:
                model_str = f.read()

            model = self.get_model_from_str(
                model_str, file_name=file_name, debug=debug,
                pre_ref_resolution_callback=pre_ref_resolution_callback,
                is_main_model=is_main_model)

            return model

        def get_model_from_str(self, model_str, file_name=None, debug=None,
                               pre_ref_resolution_callback=None,
                               is_main_model=True):
            """
            Parses given string and creates model object graph.
            """
            old_debug_state = self.debug

            try:
                if debug is not None:
                    self.debug = debug

                if self.debug:
                    self.dprint("*** PARSING MODEL ***")

                self.parse(model_str, file_name=file_name)
                # Transform parse tree to model. Skip root node which
                # represents the whole file ending in EOF.
                model = parse_tree_to_objgraph(
                    self, self.parse_tree[0], file_name=file_name,
                    pre_ref_resolution_callback=pre_ref_resolution_callback,
                    is_main_model=is_main_model)
            finally:
                if debug is not None:
                    self.debug = old_debug_state

            try:
                model._tx_metamodel = self.metamodel
            except AttributeError:
                # model is some primitive python type (e.g. str)
                pass
            return model

    return TextXModelParser(**kwargs)


def parse_tree_to_objgraph(parser, parse_tree, file_name=None,
                           pre_ref_resolution_callback=None,
                           is_main_model=True):
    """
    Transforms parse_tree to object graph representing model in a
    new language.
    """

    metamodel = parser.metamodel

    if metamodel.textx_tools_support:
        pos_rule_dict = {}
    pos_crossref_list = []

    def process_match(nt):
        """
        Process subtree for match rules.
        """
        if isinstance(nt, Terminal):
            return convert(nt.value, nt.rule_name)
        else:
            # If RHS of assignment is NonTerminal it is a product of
            # complex match rule. Convert nodes to text and do the join.
            if len(nt) > 1:
                return "".join([text(process_match(n)) for n in nt])
            else:
                return process_match(nt[0])

    def process_node(node):
        if isinstance(node, Terminal):
            return convert(node.value, node.rule_name)

        assert node.rule.root, \
            "Not a root node: {}".format(node.rule.rule_name)
        # If this node is created by some root rule
        # create metaclass instance.
        inst = None
        if not node.rule_name.startswith('__asgn'):
            # If not assignment
            # Get class
            mclass = node.rule._tx_class

            if mclass._tx_type == RULE_ABSTRACT:
                # If this meta-class is product of abstract rule replace it
                # with matched concrete meta-class down the inheritance tree.
                # Abstract meta-class should never be instantiated.
                return process_node(node[0])
            elif mclass._tx_type == RULE_MATCH:
                # If this is a product of match rule handle it as a RHS
                # of assignment and return converted python type.
                return process_match(node)

            if parser.debug:
                parser.dprint("CREATING INSTANCE {}".format(node.rule_name))

            # If user class is given
            # use it instead of generic one
            if node.rule_name in metamodel.user_classes:
                user_class = metamodel.user_classes[node.rule_name]

                # Object initialization will be done afterwards
                # At this point we need object to be allocated
                # So that nested object get correct reference
                inst = user_class.__new__(user_class)

                # Initialize object attributes for user class
                parser.metamodel._init_obj_attrs(inst, user=True)
            else:
                # Generic class will call attributes init
                # from the constructor
                inst = mclass.__new__(mclass)

                # Initialize object attributes
                parser.metamodel._init_obj_attrs(inst)

            # Collect attributes directly on meta-class instance
            obj_attrs = inst

            inst._tx_position = node.position
            inst._tx_position_end = node.position_end

            # Push real obj. and dummy attr obj on the instance stack
            parser._inst_stack.append((inst, obj_attrs))

            for n in node:
                if parser.debug:
                    parser.dprint("Recursing into {} = '{}'"
                                  .format(type(n).__name__, text(n)))
                process_node(n)

            parser._inst_stack.pop()

            # If this object is nested add 'parent' reference
            if parser._inst_stack:
                if node.rule_name in metamodel.user_classes:
                    obj_attrs._txa_parent = parser._inst_stack[-1][0]
                else:
                    obj_attrs.parent = parser._inst_stack[-1][0]

            # If the class is user supplied we need to do
            # a proper initialization at this point.
            if node.rule_name in metamodel.user_classes:
                try:
                    # Get only attributes defined by the grammar as well
                    # as `parent` if exists
                    attrs = {}
                    if hasattr(obj_attrs, '_txa_parent'):
                        attrs['parent'] = obj_attrs._txa_parent
                        del obj_attrs._txa_parent
                    for a in obj_attrs.__class__._tx_attrs:
                        attrs[a] = getattr(obj_attrs, "_txa_%s" % a)
                        delattr(obj_attrs, "_txa_%s" % a)
                    inst.__init__(**attrs)
                except TypeError as e:
                    # Add class name information in case of
                    # wrong constructor parameters
                    e.args += ("for class %s" %
                               inst.__class__.__name__,)
                    parser.dprint(traceback.print_exc())
                    raise e

            # Special case for 'name' attrib. It is used for cross-referencing
            if hasattr(inst, 'name') and inst.name:
                # Objects of each class are in its own namespace
                if not id(inst.__class__) in parser._instances:
                    parser._instances[id(inst.__class__)] = {}
                parser._instances[id(inst.__class__)][inst.name] = inst

            if parser.debug:
                parser.dprint("LEAVING INSTANCE {}".format(node.rule_name))

        else:
            # Handle assignments
            attr_name = node.rule._attr_name
            op = node.rule_name.split('_')[-1]
            model_obj, obj_attr = parser._inst_stack[-1]
            cls = type(model_obj)
            metaattr = cls._tx_attrs[attr_name]

            # Mangle attribute name to prevent name clashing with property
            # setters on user classes
            if cls.__name__ in metamodel.user_classes:
                txa_attr_name = "_txa_%s" % attr_name
            else:
                txa_attr_name = attr_name

            if parser.debug:
                parser.dprint('Handling assignment: {} {}...'
                              .format(op, txa_attr_name))

            if op == 'optional':
                setattr(obj_attr, txa_attr_name, True)

            elif op == 'plain':
                attr_value = getattr(obj_attr, txa_attr_name)
                if attr_value and type(attr_value) is not list:
                    fmt = "Multiple assignments to attribute {} at {}"
                    raise TextXSemanticError(
                        message=fmt.format(
                            attr_name, parser.pos_to_linecol(node.position)),
                        err_type=MULT_ASSIGN_ERROR)

                # Convert tree bellow assignment to proper value
                value = process_node(node[0])

                if metaattr.ref and not metaattr.cont:
                    # If this is non-containing reference create ObjCrossRef
                    value = ObjCrossRef(obj_name=value, cls=metaattr.cls,
                                        position=node[0].position)
                    parser._crossrefs.append((model_obj, metaattr, value))
                    return model_obj

                if type(attr_value) is list:
                    attr_value.append(value)
                else:
                    setattr(obj_attr, txa_attr_name, value)

            elif op in ['list', 'oneormore', 'zeroormore']:
                for n in node:
                    # If the node is separator skip
                    if n.rule_name != 'sep':
                        # Convert node to proper type
                        # Rule links will be resolved later
                        value = process_node(n)

                        if metaattr.ref and not metaattr.cont:
                            # If this is non-containing reference
                            # create ObjCrossRef

                            value = ObjCrossRef(obj_name=value,
                                                cls=metaattr.cls,
                                                position=n.position)

                            parser._crossrefs.append((obj_attr, metaattr,
                                                      value))
                            continue

                        if not hasattr(obj_attr, txa_attr_name) or \
                                getattr(obj_attr, txa_attr_name) is None:
                            setattr(obj_attr, txa_attr_name, [])
                        getattr(obj_attr, txa_attr_name).append(value)
            else:
                # This shouldn't happen
                assert False

        # Collect rules for textx-tools
        if inst and metamodel.textx_tools_support:
            pos = (inst._tx_position, inst._tx_position_end)
            pos_rule_dict[pos] = inst

        return inst

    def call_obj_processors(model_obj, metaclass=None):
        """
        Depth-first model object processing.
        """
        try:
            if metaclass is None:
                metaclass = metamodel[model_obj.__class__.__name__]
        except KeyError:
            raise TextXSemanticError(
                'Unknown meta-class "{}".'
                .format(model.obj.__class__.__name__))

        many = [MULT_ONEORMORE, MULT_ZEROORMORE]
        for metaattr in metaclass._tx_attrs.values():
            # If attribute is base type or containment reference go down
            if metaattr.is_base_type or (metaattr.ref and metaattr.cont):
                attr = getattr(model_obj, metaattr.name)
                if attr:
                    if metaattr.mult in many:
                        for idx, obj in enumerate(attr):
                            if obj:
                                result = call_obj_processors(obj,
                                                             metaattr.cls)
                                if result is not None:
                                    attr[idx] = result
                    else:
                        result = call_obj_processors(attr, metaattr.cls)
                        if result is not None:
                            setattr(model_obj, metaattr.name, result)

        obj_processor = metamodel.obj_processors.get(metaclass.__name__, None)
        if obj_processor:
            return obj_processor(model_obj)

    model = process_node(parse_tree)
    # Register filename of the model for later use (e.g. imports/scoping).
    is_primitive_type = False
    try:
        model._tx_filename = file_name
    except AttributeError:
        # model is some primitive python type (e.g. str)
        is_primitive_type = True
        pass

    if pre_ref_resolution_callback:
        pre_ref_resolution_callback(model)

    for scope_provider in metamodel.scope_providers.values():
        from textx.scoping import ModelLoader
        if isinstance(scope_provider, ModelLoader):
            scope_provider.load_models(model)

    if not is_primitive_type:
        model._tx_reference_resolver = ReferenceResolver(
            parser, model, pos_crossref_list)
        model._tx_parser = parser

    if is_main_model:
        from textx.scoping import get_all_models_including_attached_models
        models = get_all_models_including_attached_models(model)
        # filter out all models w/o resolver:
        models = list(filter(
            lambda x: hasattr(x, "_tx_reference_resolver"), models))

        resolved_count = 1
        unresolved_count = 1
        while unresolved_count > 0 and resolved_count > 0:
            resolved_count = 0
            unresolved_count = 0
            # print("***RESOLVING {} models".format(len(models)))
            for m in models:
                resolved_count_for_this_model, delayed_crossrefs = \
                    m._tx_reference_resolver.resolve_one_step()
                resolved_count += resolved_count_for_this_model
                unresolved_count += len(delayed_crossrefs)
            # print("DEBUG: delayed #:{} unresolved #:{}".
            #      format(unresolved_count,unresolved_count))
        if (unresolved_count > 0):
            error_text = "Unresolvable cross references:"

            for m in models:
                for _, _, delayed \
                        in m._tx_reference_resolver.delayed_crossrefs:
                    line, col = parser.pos_to_linecol(delayed.position)
                    error_text += ' "{}" of class "{}" at {}'.format(
                        delayed.obj_name, delayed.cls.__name__, (line, col))
            raise TextXSemanticError(error_text, line=line, col=col)

        for m in models:
            # TODO: what does this check?
            assert not m._tx_reference_resolver.parser._inst_stack

        # cleanup
        for m in models:
            del m._tx_reference_resolver

        # final check that everything went ok
        for m in models:
            assert 0 == len(get_children_of_type(Postponed.__class__, m))

        # We have model loaded and all link resolved
        # So we shall do a depth-first call of object
        # processors if any processor is defined.
        if metamodel.obj_processors:
            if parser.debug:
                parser.dprint("CALLING OBJECT PROCESSORS")
            for m in models:
                call_obj_processors(m)

    if metamodel.textx_tools_support \
            and type(model) not in PRIMITIVE_PYTHON_TYPES:
        # Cross-references for go-to definition language server support
        # Already sorted based on ref_pos_start attr
        # (required for binary search)
        model._pos_crossref_list = pos_crossref_list

        # Dict for storing rules where key is position of rule instance in text
        # Sorted based on nested rules
        model._pos_rule_dict = OrderedDict(sorted(pos_rule_dict.items(),
                                                  key=lambda x: x[0],
                                                  reverse=True))
    return model


class ReferenceResolver:
    """
    Responsability: store current model state before reference resolving.
    When all models are parsed, start resolving all references in a loop.
    """

    def __init__(self, parser, model, pos_crossref_list):
        self.parser = parser
        self.model = model
        self.pos_crossref_list = pos_crossref_list  # tool support
        self.delayed_crossrefs = []

    def has_unresolved_crossrefs(self, obj, attr_name=None):
        """
        Args:
            obj: has this object unresolved crossrefs in its fields
            (non recursively)

        Returns:
            True (has unresolved crossrefs) or False (else)
        """
        if get_model(obj) != self.model:
            return get_model(obj). \
                _tx_reference_resolver.has_unresolved_crossrefs(obj)
        else:
            for crossref_obj, attr, crossref in self.parser._crossrefs:
                if crossref_obj is obj:
                    if (not attr_name) or attr_name == attr.name:
                        return True
            return False

    def resolve_one_step(self):
        """
        Resolves model references.
        """
        metamodel = self.parser.metamodel

        current_crossrefs = self.parser._crossrefs
        # print("DEBUG: Current crossrefs #: {}".
        #      format(len(current_crossrefs)))
        new_crossrefs = []
        self.delayed_crossrefs = []
        resolved_crossref_count = 0

        # -------------------------
        # start of resolve-loop
        # -------------------------
        default_scope = DefaultScopeProvider()
        for obj, attr, crossref in current_crossrefs:
            if (get_model(obj) == self.model):
                attr_value = getattr(obj, attr.name)
                attr_refs = [obj.__class__.__name__ + "." + attr.name,
                             "*." + attr.name, obj.__class__.__name__ + ".*",
                             "*.*"]
                for attr_ref in attr_refs:
                    if attr_ref in metamodel.scope_providers:
                        if self.parser.debug:
                            self.parser.dprint(" FOUND {}".format(attr_ref))
                        resolved = metamodel.scope_providers[attr_ref](
                            obj, attr, crossref)
                        break
                else:
                    resolved = default_scope(obj, attr, crossref)

                # Collect cross-references for textx-tools
                if resolved and not type(resolved) is Postponed:
                    if metamodel.textx_tools_support:
                        self.pos_crossref_list.append(
                            RefRulePosition(
                                name=crossref.obj_name,
                                ref_pos_start=crossref.position,
                                ref_pos_end=crossref.position + len(
                                    resolved.name),
                                def_pos_start=resolved._tx_position,
                                def_pos_end=resolved._tx_position_end))

                if not resolved:
                    # As a fall-back search builtins if given
                    if metamodel.builtins:
                        if crossref.obj_name in metamodel.builtins:
                            # TODO: Classes must match
                            resolved = metamodel.builtins[crossref.obj_name]

                if not resolved:
                    line, col = self.parser.pos_to_linecol(crossref.position)
                    raise TextXSemanticError(
                        message='Unknown object "{}" of class "{}"'.format(
                            crossref.obj_name, crossref.cls.__name__),
                        line=line, col=col, err_type=UNKNOWN_OBJ_ERROR,
                        expected_obj_cls=crossref.cls,
                        filename=self.model._tx_filename)

                if type(resolved) is Postponed:
                    self.delayed_crossrefs.append((obj, attr, crossref))
                    new_crossrefs.append((obj, attr, crossref))
                else:
                    resolved_crossref_count += 1
                    if attr.mult in [MULT_ONEORMORE, MULT_ZEROORMORE]:
                        attr_value.append(resolved)
                    else:
                        setattr(obj, attr.name, resolved)
            else:  # crossref not in model
                new_crossrefs.append((obj, attr, crossref))
        # -------------------------
        # end of resolve-loop
        # -------------------------
        # store cross-refs from other models in the parser list (for later
        # processing)
        self.parser._crossrefs = new_crossrefs
        # print("DEBUG: Next crossrefs #: {}".format(len(new_crossrefs)))
        return (resolved_crossref_count, self.delayed_crossrefs)
