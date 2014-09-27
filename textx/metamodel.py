#######################################################################
# Name: metamodel.py
# Purpose: Meta-model construction.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

import codecs
import os
from .textx import language_from_str, python_type, BASE_TYPE_NAMES, ID, BOOL,\
    INT, FLOAT, STRING, NUMBER, BASETYPE
from .const import MULT_ONE, MULT_ZEROORMORE, MULT_ONEORMORE, RULE_NORMAL


class MetaAttr(object):
    """
    A metaclass for attribute description.

    Attributes:
        name(str): Attribute name.
        cls(str, TextXClass or base python type): The type of the attribute.
        mult(str): Multiplicity
        cont(bool): Is this attribute contained inside object.
        ref(bool): Is this attribute a reference. If it is not a reference
            it must be containment.
        position(int): A position in the input string where attribute is
            defined.
    """
    def __init__(self, name, cls=None, mult=MULT_ONE, cont=True, ref=False,
                 position=0):
        self.name = name
        self.cls = cls
        self.mult = mult
        self.cont = cont
        self.ref = ref
        self.position = position


class TextXClass(object):
    """Base class for all language classes."""
    pass


class TextXMetaModel(object):
    """
    Meta-model contains all information about language abstract syntax.
    Furthermore, this class is in charge for model instantiation and new
    language class creation.
    This class inherits dictionary as is used for language class lookup.

    Attributes:
        rootcls(TextXClass): A language class that is a root of the metamodel.
        namespaces(dict): A dict from abs. file name to the dict in the form
            {clsname: (cls, rule), clsname:(cls, rule)} that holds meta-classes
            and peg rules imported from the given grammar file.
            Special key 'base' is used for BASETYPE classes. None key is used
            for all classes imported from the grammar given as a string.
        namespace_stack(list): A stack of namespace names (usually absolute
            filenames). Used to keep track of the current namespace.
        imported_namespaces(dict): A dict from namespace name to the list of
            references to imported namespaces. Used in searches for the
            unqualified rules.
        builtins(dict): A dict of named object used in linking phase.
            References to named objects not defined in the model will be
            searched here.
    """

    def __init__(self, file_name=None, classes=None, builtins=None,
                 debug=False):
        """
        Args:
            file_name(str): A file name if meta-model is going to be
                constructed from file or None otherwise.
            root_dir(str): Absolute directory used as a root for relative
                grammar imports. If not given file_name dir is used if given.
            classes(dict of python classes): Custom meta-classes used
                instead of generic ones.
            builtins(dict of named objects): Named objects used in linking
                phase. This objects are part of each model.
            debug(bool): Should debug messages be printed.
        """

        self.file_name = file_name
        self.rootcls = None

        self.builtins = builtins

        if classes:
            self.update(classes)

        # Registered model processors
        self._model_processors = []

        # Namespaces
        self.namespaces = {}
        self.namespace_stack = []

        # Imported namespaces
        self.imported_namespaces = {}

        # Create new namespace for BASETYPE classes
        self.enter_namespace('base')

        # Base types hierarchy should exist in each meta-model
        base_id = self.new_class('ID', ID, 0)
        base_string = self.new_class('STRING', STRING, 0)
        base_bool = self.new_class('BOOL', BOOL, 0)
        base_int = self.new_class('INT', INT, 0)
        base_float = self.new_class('FLOAT', FLOAT, 0)
        base_number = self.new_class('NUMBER', NUMBER, 0,
                                     [base_int, base_float])
        self.new_class('BASETYPE', BASETYPE, 0,
                       [base_number, base_id, base_string, base_bool])

        # If file_name is given its absolute path will be a namespace
        if file_name:
            file_name = os.path.abspath(file_name)

        # Enter namespace for given file or None if metamodel is
        # constructed from string.
        self.enter_namespace(file_name)

    def enter_namespace(self, namespace_name):
        """
        A namespace is usually an absolute file name of the grammar.
        A special namespace 'base' is used for BASETYPE namespace.
        """
        if namespace_name not in self.namespaces:
            self.namespaces[namespace_name] = {}

            # BASETYPE namespace is imported in each namespace
            self.imported_namespaces[namespace_name] = \
                [self.namespaces['base']]

        self.namespace_stack.append(namespace_name)

    def leave_namespace(self):
        """
        Leaves current namespace (i.e. grammar file).
        """
        self.namespace_stack.pop()

    def new_import(self, import_name):
        """
        Starts a new import.
        Args:
            import_name(str): A relative import in the dot syntax
                (e.g. "first.second.expressions")
        """

        # Find the absolute file name of the import based on the relative
        # import_name and current grammar file (namespace)
        current_namespace = self.namespace_stack[-1]
        current_dir = ''
        if current_namespace and current_namespace != 'base':
            current_dir = os.path.dirname(current_namespace)
        import_file_name = "%s.tx" % os.path.join(current_dir,
                                                  *import_name.split("."))

        if import_file_name not in self.namespaces:
            self.enter_namespace(import_file_name)
            metamodel_from_file(import_file_name, metamodel=self)
            self.leave_namespace()

        # Add the import to the imported_namespaces for current namespace
        # so that resolving of current grammar searches imported grammars
        # in the order of import
        self.imported_namespaces[current_namespace].append(
            self.namespaces[import_file_name])

    def new_class(self, name, peg_rule, position, inherits=None, root=False):
        """
        Creates a new class with the given name in the current namespace.
        Args:
            name(str): The name of the class.
            peg_rule(ParserExpression): An arpeggio peg rule used to match
                this class.
            positon(int): A position in the input where class is defined.
            root(bool): Is this class a root class of the metamodel.
        """

        class Meta(TextXClass):
            """
            Dynamic metaclass. Each textX rule will result in creating
            one Meta class with the type name of the rule.
            Model is a graph of python instances of this metaclasses.
            Attributes:
                _attrs(dict): A dict of meta-attributes keyed by name.
                _inh_by(list): Classes that inherits this one.
                _position(int): A position in the input string where this
                    class is defined.
                _type(int): The type of the textX rule this class is created
                    for. See textx.const
                _metamodel(TextXMetaModel): A metamodel this class belongs to.
                _fqtn(str): A fully qualified type name.
                    A property calculated using namespace of containing
                    meta-model.
            """
            # Attribute information (MetaAttr instances) keyed by name.
            _attrs = {}

            # A list of inheriting classes
            _inh_by = inherits if inherits else []

            _position = position

            # The type of the rule this meta-class results from.
            # There are three rule types: normal, abstract and match
            _type = RULE_NORMAL

            def __init__(self):
                """
                Initializes attributes.
                """
                for attr in self._attrs.values():
                    if attr.mult in [MULT_ZEROORMORE, MULT_ONEORMORE]:
                        # list
                        setattr(self, attr.name, [])
                    elif attr.cls.__name__ in BASE_TYPE_NAMES:
                        # Instantiate base python type
                        setattr(self, attr.name,
                                python_type(attr.cls.__name__)())
                    else:
                        # Reference to other obj
                        setattr(self, attr.name, None)

            @classmethod
            def new_attr(clazz, name, cls=None, mult=MULT_ONE, cont=True,
                         ref=False, position=0):
                """Creates new meta attribute of this class."""
                attr = MetaAttr(name, cls, mult, cont, ref, position)
                clazz._attrs[name] = attr
                return attr

        cls = Meta
        cls.__name__ = name
        cls._metamodel = self

        cls._typename = cls.__name__

        # Push this class and PEG rule in the current namespace
        current_namespace = self.namespaces[self.namespace_stack[-1]]
        current_namespace[name] = (cls, peg_rule)

        if root:
            self.rootcls = cls

        return cls

    def __getitem__(self, name):
        """
        Search for and return class and peg_rule with the given name.
        Returns:
            TextXClass, ParsingExpression
        """
        if "." in name:
            # Name is fully qualified
            # Find the absolute file from the current namespace and
            # the fully qualified name.
            namespace = self._fqn_to_namespace(name)
            name = name.split(".")[-1]
            return self.namespaces[namespace][name]
        else:
            # If not fully qualified search in the current namespace
            # and after that in the imported_namespaces
            if name in self.current_namespace:
                return self.current_namespace[name]

            for namespace in \
                    self.imported_namespaces[self.namespace_stack[-1]]:
                if name in namespace:
                    return namespace[name]

            raise KeyError

    def __iter__(self):
        """
        Iterate over all classes in the current namespace and imported
        namespaces.
        """

        # Current namespace
        for name in self.current_namespace:
            yield self.current_namespace[name]

        # Imported namespaces
        for namespace in \
                self.imported_namespaces[self.namespace_stack[-1]]:
            for name in namespace:
                # yield class, rule pair
                yield namespace[name]

    def __contains__(self, name):
        """
        Check if given name is contained in the current namespace.
        The name can be fully qualified.
        """
        try:
            self[name]
            return True
        except KeyError:
            return False

    @property
    def current_namespace(self):
        return self.namespaces[self.namespace_stack[-1]]

    def _fqn_to_namespace(self, fqn):
        """
        Based on current namespace and given fqn returns the absolute
        filename of the fqn cls grammar file.
        Args:
            fqn(str): A fully qualified name of the class.
        Returns:
            An absolute file name of the grammar fqn rule/class came from.
        """

        current_namespace = self.namespace_stack[-1]
        current_dir = ''
        if current_namespace and current_namespace != 'base':
            current_dir = os.path.dirname(current_namespace)
        namespace = "%s.tx" % os.path.join(current_dir,
                                           *(fqn.split("."))[:-1])

        return namespace

    def model_from_str(self, model_str):
        """
        Instantiates model from the given string.
        """
        model = self.parser.get_model_from_str(model_str)
        for p in self._model_processors:
            p(model, self)
        return model

    def model_from_file(self, file_name):
        """
        Instantiates model from the given file.
        """
        model = self.parser.get_model_from_file(file_name)
        for p in self._model_processors:
            p(model, self)
        return model

    def register_model_processor(self, model_processor):
        """
        Model processor is callable that will be called after
        each successful model parse.
        This callable receives model and meta-model as its parameters.
        """
        self._model_processors.append(model_processor)


def metamodel_from_str(lang_desc, classes=None, builtins=None, file_name=None,
                       root_dir=None, metamodel=None, debug=False):
    """
    Creates a new metamodel from the textX description given as a string.

    Args:
        lang_desc(str): A textX language description.
        classes(dict): An optional dict of classes used instead of
            generic ones.
        builtins(dict): An optional dict of named object used in linking phase.
            References to named object not defined in the model will be
            searched here.
        file_name(str): A file name if meta-model was loaded from file.
        metamodel(TextXMetaModel): A metamodel that should be used.
        debug(bool): Print debugging informations.
    """
    if not metamodel:
        metamodel = TextXMetaModel(file_name=file_name, classes=classes,
                                   builtins=builtins, debug=debug)

    language_from_str(lang_desc, metamodel, debug=debug)

    return metamodel


def metamodel_from_file(file_name, classes=None, builtins=None, metamodel=None,
                        debug=False):
    """
    Creates new metamodel from the given file.

    Args:
        file_name(str): The name of the file with textX language description.
        classes, builtins, metamodel, debug: See metamodel_from_str.
    """
    with codecs.open(file_name, 'r', 'utf-8') as f:
        lang_desc = f.read()

    metamodel = metamodel_from_str(lang_desc=lang_desc, classes=classes,
                                   builtins=builtins, file_name=file_name,
                                   metamodel=metamodel, debug=debug)

    return metamodel
