#######################################################################
# Name: model.py
# Purpose: Model construction.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

import sys
if sys.version < '3':
    text = unicode
else:
    text = str
import codecs
import traceback
from arpeggio import Parser, Sequence, NoMatch, EOF, Terminal
from .exceptions import TextXSyntaxError, TextXSemanticError
from .const import MULT_ONE, MULT_ONEORMORE, MULT_ZEROORMORE, RULE_NORMAL,\
    RULE_ABSTRACT


def convert(value, _type):
    """
    Convert instances of textx types to python types.
    """
    return {
            'BOOL'  : lambda x: x == '1' or x.lower() == 'true',
            'INT'   : lambda x: int(x),
            'FLOAT' : lambda x: float(x),
            'STRING': lambda x: x.strip('"\''),
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
                nodes=[top_rule, EOF()], rule_name='ModelFile', root=True)
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

        def get_model_from_file(self, file_name, encoding):
            """
            Creates model from the parse tree from the previous parse call.
            If file_name is given file will be parsed before model
            construction.
            """
            with codecs.open(file_name, 'r', encoding) as f:
                model_str = f.read()

            model = self.get_model_from_str(model_str, file_name=file_name)

            # Register filename of the model for later use.
            try:
                model._filename = file_name
            except AttributeError:
                # model is some primitive python type (e.g. str)
                pass
            return model

        def get_model_from_str(self, model_str, file_name=None):
            """
            Parses given string and creates model object graph.
            """
            if self.debug:
                print("*** MODEL ***")
            self.parse(model_str, file_name=file_name)
            # Transform parse tree to model. Skip root node which
            # represents the whole file ending in EOF.
            model = parse_tree_to_objgraph(self, self.parse_tree[0])
            try:
                model._filename = None
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

    def process_node(node):
        if isinstance(node, Terminal):
            return convert(node.value, node.rule_name)

        assert node.rule.root,\
            "Not a root node: {}".format(node.rule.rule_name)
        # If this node is created by some root rule
        # create metaclass instance.
        inst = None
        if not node.rule_name.startswith('__asgn'):
            # If not assignment
            # Get class
            mclass = metamodel[node.rule_name]

            # If there is no attributes collected it is an abstract rule
            # Skip it.
            if not mclass._attrs:
                return process_node(node[0])

            if parser.debug:
                print("CREATING INSTANCE {}".format(node.rule_name))

            # If user class is given
            # use it instead of generic one
            if node.rule_name in metamodel.user_classes:
                user_class = metamodel.user_classes[node.rule_name]

                # Object initialization will be done afterwards
                # At this point we need object to be allocated
                # So that nested object get correct reference
                inst = user_class.__new__(user_class)

                # This will serve as a dummy object to collect attribute
                # values used in constructor call.
                obj_attrs = mclass()
            else:
                # Generic class will call attributes init
                # from the constructor
                inst = mclass()

                # Collect attributes directly on meta-class instance
                obj_attrs = inst

            inst._position = node.position

            # Push real obj. and dummy attr obj on the instance stack
            parser._inst_stack.append((inst, obj_attrs))

            for n in node:
                if parser.debug:
                    print("Recursing into {} = '{}'"
                          .format(type(n).__name__, text(n)))
                process_node(n)

            parser._inst_stack.pop()

            # If this object is nested add 'parent' reference
            if parser._inst_stack:
                obj_attrs.parent = parser._inst_stack[-1][0]

            # If the class is user supplied we need to done
            # proper initialization at this point.
            if node.rule_name in metamodel.user_classes:
                try:
                    inst.__init__(**obj_attrs.__dict__)
                except TypeError as e:
                    # Add class name information in case of
                    # wrong constructor parameters
                    # print("Constructor params: {}".format(text(obj_attrs.__dict__)))
                    e.args += ("for class %s" %
                               inst.__class__.__name__,)
                    print(traceback.print_exc())
                    raise e

            # Special case for 'name' attrib. It is used for cross-referencing
            if hasattr(inst, 'name') and inst.name:
                # Objects of each class are in its own namespace
                if not id(inst.__class__) in parser._instances:
                    parser._instances[id(inst.__class__)] = {}
                parser._instances[id(inst.__class__)][inst.name] = inst

            if parser.debug:
                print("LEAVING INSTANCE {}".format(node.rule_name))

        else:
            # Handle assignments
            attr_name = node.rule._attr_name
            op = node.rule_name.split('_')[-1]
            model_obj, obj_attr = parser._inst_stack[-1]
            cls = metamodel[model_obj.__class__.__name__]
            metaattr = cls._attrs[attr_name]

            if parser.debug:
                print('Handling assignment: {} {}...'.format(op, attr_name))

            if op == 'optional':
                setattr(obj_attr, attr_name, True)

            elif op == 'plain':
                attr_value = getattr(obj_attr, attr_name)
                if attr_value and type(attr_value) is not list:
                    raise TextXSemanticError(
                        "Multiple assignments to attribute {} at {}"
                        .format(attr_name,
                                parser.pos_to_linecol(node.position)))

                # Recurse and convert value to proper type
                value = process_node(node[0])

                if metaattr.ref and not metaattr.cont:
                    # If this is non-containing reference create ObjCrossRef
                    value = ObjCrossRef(obj_name=value, cls=metaattr.cls,
                                        position=node[0].position)

                if type(attr_value) is list:
                    attr_value.append(value)
                else:
                    setattr(obj_attr, attr_name, value)

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

                        if not hasattr(obj_attr, attr_name) or \
                                getattr(obj_attr, attr_name) is None:
                            setattr(obj_attr, attr_name, [])
                        getattr(obj_attr, attr_name).append(value)
            else:
                # This shouldn't happen
                assert False

        return inst

    def resolve_refs(model):
        """
        Resolves obj cross refs.
        """
        # TODO: Scoping and name-space rules.

        resolved_set = set()
        metamodel = parser.metamodel

        def _resolve_ref(obj_ref):
            if obj_ref is None:
                return
            assert type(obj_ref) is ObjCrossRef, type(obj_ref)
            if parser.debug:
                print("Resolving obj crossref: {}:{}"
                      .format(obj_ref.cls, obj_ref.obj_name))

            def _resolve_ref_abstract(obj_cls):
                """
                Depth-first resolving of abstract rules.
                """
                for inherited in obj_cls._inh_by:
                    if inherited._type == RULE_ABSTRACT:
                        return _resolve_ref_abstract(inherited)
                    elif inherited._type == RULE_NORMAL:
                        if id(inherited) in parser._instances:
                            objs = parser._instances[id(inherited)]
                            if obj_ref.obj_name in objs:
                                return objs[obj_ref.obj_name]

            if obj_ref.cls._type == RULE_NORMAL:
                if id(obj_ref.cls) in parser._instances:
                    objs = parser._instances[id(obj_ref.cls)]
                    if obj_ref.obj_name in objs:
                        return objs[obj_ref.obj_name]
            elif obj_ref.cls._type == RULE_ABSTRACT:
                # For abstract rule ref do a depth first search on
                # the inheritance tree to find normal rules
                # and return a first instance of that meta-class instance with
                # the referred name.
                obj = _resolve_ref_abstract(obj_ref.cls)
                if obj:
                    return obj
            else:
                pass
                # TODO: Match rules cannot be referred. This is
                #       an error in language description.

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

        def _resolve(o):
            if parser.debug:
                print("RESOLVING CLASS: {}".format(o.__class__.__name__))
            if o in resolved_set:
                return
            resolved_set.add(o)

            # If this object has attributes (created using a normal rule)
            if hasattr(o.__class__, "_attrs"):
                for attr in o.__class__._attrs.values():
                    if parser.debug:
                        print("RESOLVING ATTR: {}".format(attr.name))
                        print("mult={}, ref={}, con={}".format(
                            attr.mult,
                            attr.ref, attr.cont))
                    attr_value = getattr(o, attr.name)
                    if attr.mult in [MULT_ONEORMORE, MULT_ZEROORMORE]:
                        for idx, list_attr_value in enumerate(attr_value):
                            if attr.ref:
                                if attr.cont:
                                    _resolve(list_attr_value)
                                else:
                                    attr_value[idx] = \
                                        _resolve_ref(list_attr_value)
                    else:
                        if attr.ref:
                            if attr.cont:
                                _resolve(attr_value)
                            else:
                                setattr(o, attr.name, _resolve_ref(attr_value))

        _resolve(model)

    def call_obj_processors(model_obj):
        """
        Depth-first model object processing.
        """
        metaclass = metamodel[model_obj.__class__.__name__]

        for metaattr in metaclass._attrs.values():
            # If attribute is containment reference
            # go down
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
            print("CALLING OBJECT PROCESSORS")
        call_obj_processors(model)

    return model
