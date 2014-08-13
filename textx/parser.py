from arpeggio import Parser, Sequence, NoMatch, EOF, Terminal
from textx.exceptions import TextXSyntaxError

CONSTRUCTORS = {
        'ID': str,
        'BOOL': bool,
        'INT' : int,
        'FLOAT': float,
        'STRING': str,
        'LIST': list,
        }
def convert(value, _type):
    return {
            'BOOL'  : lambda x: x=='1' or x.lower()=='true',
            'INT'   : lambda x: int(x),
            'FLOAT' : lambda x: float(x),
            'STRING': lambda x: x.strip('"\''),
            }.get(_type, lambda x: x)(value)

def get_language_parser(top_rule, comments_model, debug=False):
    class TextXLanguageParser(Parser):
        """
        Parser created from textual textX language description.
        Semantic actions for this parser will construct object
        graph representing model on the given language.
        """
        def __init__(self, *args, **kwargs):
            super(TextXLanguageParser, self).__init__(*args, **kwargs)

            # By default first rule is starting rule
            # and must be followed by the EOF
            self.parser_model = Sequence(nodes=[top_rule, EOF()],\
                    rule_name='ModelFile', root=True)
            self.comments_model = comments_model

            # Stack for metaclass instances
            self._inst_stack = []
            # Dict for cross-ref resolving
            self._instances = {}

            self.debug = debug

        def _parse(self):
            try:
                return self.parser_model.parse(self)
            except NoMatch as e:
                raise TextXSyntaxError(str(e))

        def get_model(self, file_name=None):
            """
            Creates model from the parse tree from the previous parse call.
            If file_name is given file will be parsed before model construction.
            """
            if self.debug:
                print("*** MODEL ***")

            if file_name:
                self.parse_file(file_name)

            # Transform parse tree to model. Skip root node which
            # represents the whole file ending in EOF.
            model = parse_tree_to_objgraph(self, self.parse_tree[0])
            model._metacls_info = self._metacls_info
            return model

        def get_metamodel(self):
            return self._metacls_info

    return TextXLanguageParser()


def parse_tree_to_objgraph(parser, parse_tree):
    """
    Transforms parse_tree to object graph representing model in a
    new language.
    """

    def process_node(node):
        if isinstance(node, Terminal):
            return convert(node.value, node.rule_name)

        assert node.rule.root, "Not a root node: {}".format(node.rule.rule_name)
        # If this node is created by some root rule
        # create metaclass instance.
        inst = None
        if not node.rule_name.startswith('__asgn'):
            # If not assignment
            # Create metaclass instance
            metacls_info = parser._metacls_info[node.rule_name]
            mclass = metacls_info.metacls

            # If there is no attributes collected it is an abstract rule
            # Skip it.
            if not metacls_info.attrib_types:
                return process_node(node[0])

            if parser.debug:
                print("CREATING INSTANCE {}".format(node.rule_name))

            inst = mclass()
            # Initialize attributes
            for attr_name, constructor in metacls_info.attrib_types.items():
                init_value = CONSTRUCTORS[constructor]()\
                        if constructor in CONSTRUCTORS else None
                setattr(inst, attr_name, init_value)

            parser._inst_stack.append(inst)

            for n in node:
                if parser.debug:
                    print("Recursing into {} = '{}'".format(type(n).__name__, str(n)))
                process_node(n)

            old = parser._inst_stack.pop()

            # Special case for 'name' attrib. It is used for cross-referencing
            if hasattr(inst, 'name') and inst.name:
                inst.__name__ = inst.name
                parser._instances[inst.name] = inst

            if parser.debug:
                old_str = "{}(name={})".format(type(old).__name__, old.name)  \
                        if hasattr(old, 'name') else type(old).__name__
                print("LEAVING INSTANCE {}".format(old_str))

        else:
            # Handle assignments
            attr_name = node.rule._attr_name
            op = node.rule_name.split('_')[-1]
            i = parser._inst_stack[-1]

            if parser.debug:
                print('Handling assignment: {} {}...'.format(op, attr_name))

            if op == 'optional':
                setattr(i, attr_name, True)

            elif op == 'plain':
                attr = getattr(i, attr_name)
                if attr and type(attr) is not list:
                    raise TextXSemanticError("Multiple assignments to meta-attribute {} at {}"\
                            .format(attr_name, parser.pos_to_linecol(node.position)))

                # Recurse and convert value to proper type
                value = convert(process_node(node[0]), node[0].rule_name)
                if parser.debug:
                    print("{} = {}".format(attr_name, value))
                if type(attr) is list:
                    attr.append(value)
                else:
                    setattr(i, attr_name, value)

            elif op in ['list', 'oneormore', 'zeroormore']:
                for n in node:
                    # If the node is separator skip
                    if n.rule_name != 'sep':
                        # Convert node to proper type
                        # Rule links will be resolved later
                        value = convert(process_node(n), n.rule_name)
                        if parser.debug:
                            print("{}:{}[] = {}".format(type(i).__name__, 
                                attr_name, value))

                        if not hasattr(i, attr_name) or getattr(i, attr_name) is None:
                            setattr(i, attr_name, [])
                        getattr(i, attr_name).append(value)
            else:
                # This shouldn't happen
                assert False

        return inst

    def resolve_refs(model):
        """
        Resolves obj cross refs.
        """
        resolved_set = set()
        metaclass_info = parser._metacls_info

        def _resolve(o):
            if o in resolved_set:
                return
            resolved_set.add(o)

            if not type(o).__name__ in metaclass_info:
                return

            metacls = metaclass_info[type(o).__name__]

            refs_cont_names = [ref[0] \
                        for ref in chain(metacls.refs, metacls.cont)]

            for ref_name in refs_cont_names:
                value = getattr(o, ref_name)
                attr_type = metacls.attrib_types[ref_name]
                if attr_type == 'LIST':
                    for idx, ref_val in enumerate(value):
                        if type(ref_val) is str:
                            target_obj = parser._instances[ref_val]
                            value[idx] = target_obj
                            _resolve(target_obj)
                        else:
                            _resolve(ref_val)
                else:
                    if type(value) is str:
                        target_obj = parser._instances[value]
                        setattr(o, ref_name, target_obj)
                        _resolve(target_obj)
                    else:
                        _resolve(value)

        _resolve(model)


    model = process_node(parse_tree)
    # model = resolve_refs(model)
    assert not parser._inst_stack

    return model

