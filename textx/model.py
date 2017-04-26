#######################################################################
# Name: model.py
# Purpose: Model construction.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

import sys
import codecs
import traceback
from arpeggio import Parser, Sequence, NoMatch, EOF, Terminal
from .exceptions import TextXSyntaxError, TextXSemanticError
from .const import MULT_OPTIONAL, MULT_ONE, MULT_ONEORMORE, MULT_ZEROORMORE, \
    RULE_COMMON, RULE_ABSTRACT, RULE_MATCH
from .textx import PRIMITIVE_PYTHON_TYPES
if sys.version < '3':
    text = unicode
else:
    text = str

__all__ = ['children_of_type', 'parent_of_type', 'model_root', 'metamodel']


def model_root(obj):
    """
    Finds model root element for the given object.
    """
    p = obj
    while hasattr(p, 'parent'):
        p = p.parent
    return p


def metamodel(obj):
    """
    Returns metamodel of the given object's model.
    """
    return model_root(obj)._tx_metamodel


def parent_of_type(typ, obj):
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


def children_of_type(typ, root):
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

    collected = []

    if type(typ) is not text:
        typ = typ.__name__

    def follow(elem):

        if elem in collected:
            return

        if elem.__class__.__name__ == typ:
            collected.append(elem)

        # Use meta-model to search for all contained child elements.
        cls = elem.__class__

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

        def _parse(self):
            try:
                return self.parser_model.parse(self)
            except NoMatch as e:
                line, col = e.parser.pos_to_linecol(e.position)
                raise TextXSyntaxError(text(e), line, col)

        def get_model_from_file(self, file_name, encoding, debug):
            """
            Creates model from the parse tree from the previous parse call.
            If file_name is given file will be parsed before model
            construction.
            """
            with codecs.open(file_name, 'r', encoding) as f:
                model_str = f.read()

            model = self.get_model_from_str(model_str, file_name=file_name,
                                            debug=debug)

            # Register filename of the model for later use.
            try:
                model._tx_filename = file_name
            except AttributeError:
                # model is some primitive python type (e.g. str)
                pass
            return model

        def get_model_from_str(self, model_str, file_name=None, debug=None):
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
                model = parse_tree_to_objgraph(self, self.parse_tree[0])
            finally:
                if debug is not None:
                    self.debug = old_debug_state

            try:
                model._tx_filename = None
                model._tx_metamodel = self.metamodel
            except AttributeError:
                # model is some primitive python type (e.g. str)
                pass
            return model

    return TextXModelParser(**kwargs)


def parse_tree_to_objgraph(parser, parse_tree):
    """
    Transforms parse_tree to object graph representing model in a
    new language.
    """

    metamodel = parser.metamodel

    def process_match(nt):
        """
        Process subtree for match rules.
        """
        if isinstance(nt, Terminal):
            return metamodel.convert(nt.value, nt.rule_name)
        else:
            # If RHS of assignment is NonTerminal it is a product of
            # complex match rule. Convert nodes to text and do the join.
            if len(nt) > 1:
                return metamodel.convert(
                    "".join([text(process_match(n)) for n in nt]),
                    nt.rule_name)
            else:
                return process_match(nt[0])

    def process_node(node):
        if isinstance(node, Terminal):
            return metamodel.convert(node.value, node.rule_name)

        assert node.rule.root,\
            "Not a root node: {}".format(node.rule.rule_name)
        # If this node is created by some root rule
        # create metaclass instance.
        inst = None
        if not node.rule_name.startswith('__asgn'):
            # If not assignment
            # Get class
            mclass = metamodel[node.rule_name]

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
                    # print("Constructor params: {}".format(text(obj_attrs.__dict__)))
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
            cls = metamodel[model_obj.__class__.__name__]
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
                    raise TextXSemanticError(
                        "Multiple assignments to attribute {} at {}"
                        .format(attr_name,
                                parser.pos_to_linecol(node.position)))

                # Convert tree bellow assignment to proper value
                value = process_node(node[0])

                if metaattr.ref and not metaattr.cont:
                    # If this is non-containing reference create ObjCrossRef
                    value = ObjCrossRef(obj_name=value, cls=metaattr.cls,
                                        position=node[0].position)

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
                                                position=node[0].position)

                        if not hasattr(obj_attr, txa_attr_name) or \
                                getattr(obj_attr, txa_attr_name) is None:
                            setattr(obj_attr, txa_attr_name, [])
                        getattr(obj_attr, txa_attr_name).append(value)
            else:
                # This shouldn't happen
                assert False

        return inst

    def resolve_refs(model):
        """
        Resolves model references.
        """
        # TODO: Scoping and name-space rules.

        resolved_set = set()
        metamodel = parser.metamodel

        def _resolve_link_rule_ref(obj_ref):

            if obj_ref is None:
                return

            assert type(obj_ref) is ObjCrossRef, type(obj_ref)

            if parser.debug:
                parser.dprint("Resolving obj crossref: {}:{}"
                              .format(obj_ref.cls, obj_ref.obj_name))

            def _inner_resolve_link_rule_ref(cls, obj_name):
                """
                Depth-first resolving of link rule reference.
                """
                if cls._tx_type is RULE_ABSTRACT:
                    for inherited in cls._tx_inh_by:
                        result = _inner_resolve_link_rule_ref(inherited,
                                                              obj_name)
                        if result:
                            return result
                elif cls._tx_type == RULE_COMMON:
                    if id(cls) in parser._instances:
                        objs = parser._instances[id(cls)]
                        if obj_name in objs:
                            return objs[obj_name]

            result = _inner_resolve_link_rule_ref(obj_ref.cls,
                                                  obj_ref.obj_name)
            if result:
                return result

            # As a fall-back search builtins if given
            if metamodel.builtins:
                if obj_ref.obj_name in metamodel.builtins:
                    # TODO: Classes must match
                    return metamodel.builtins[obj_ref.obj_name]

            line, col = parser.pos_to_linecol(obj_ref.position)
            raise TextXSemanticError(
                'Unknown object "{}" of class "{}" at {}'
                .format(obj_ref.obj_name, obj_ref.cls.__name__, (line, col)),
                line=line, col=col)

        def _resolve_obj_attributes(o):
            if parser.debug:
                parser.dprint("RESOLVING CLASS: {}"
                              .format(o.__class__.__name__))
            if o in resolved_set:
                return
            resolved_set.add(o)

            # If this object has attributes (created using a common rule)
            if hasattr(o.__class__, "_tx_attrs"):
                for attr in o.__class__._tx_attrs.values():
                    if parser.debug:
                        parser.dprint("RESOLVING ATTR: {}".format(attr.name))
                        parser.dprint("mult={}, ref={}, con={}".format(
                                      attr.mult,
                                      attr.ref, attr.cont))
                    attr_value = getattr(o, attr.name)
                    if attr.mult in [MULT_ONEORMORE, MULT_ZEROORMORE]:
                        for idx, list_attr_value in enumerate(attr_value):
                            if attr.ref:
                                if attr.cont:
                                    _resolve_obj_attributes(list_attr_value)
                                else:
                                    attr_value[idx] = \
                                        _resolve_link_rule_ref(list_attr_value)
                    else:
                        if attr.ref:
                            if attr.cont:
                                _resolve_obj_attributes(attr_value)
                            else:
                                setattr(o, attr.name,
                                        _resolve_link_rule_ref(attr_value))

        _resolve_obj_attributes(model)

    def call_obj_processors(model_obj):
        """
        Depth-first model object processing.
        """

        if type(model_obj) in PRIMITIVE_PYTHON_TYPES:
            metaclass = type(model_obj)
        else:
            metaclass = metamodel[model_obj.__class__.__name__]

            for metaattr in metaclass._tx_attrs.values():
                # If attribute is containment reference go down
                if metaattr.ref and metaattr.cont:
                    attr = getattr(model_obj, metaattr.name)
                    if attr:
                        if metaattr.mult != MULT_ONE:
                            for obj in attr:
                                if obj:
                                    call_obj_processors(obj)
                        else:
                            call_obj_processors(attr)

        obj_processor = metamodel.obj_processors.get(metaclass.__name__, None)
        if obj_processor:
            obj_processor(model_obj)

    model = process_node(parse_tree)
    resolve_refs(model)
    assert not parser._inst_stack

    # We have model loaded and all link resolved
    # So we shall do a depth-first call of object
    # processors if any processor is defined.
    if metamodel.obj_processors:
        if parser.debug:
            parser.dprint("CALLING OBJECT PROCESSORS")
        call_obj_processors(model)

    return model
