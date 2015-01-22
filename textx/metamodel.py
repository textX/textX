#######################################################################
# Name: metamodel.py
# Purpose: Meta-model construction.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

import codecs
import os
from collections import OrderedDict
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
        bool_assignment(bool): Is this attribute specified using bool
            assignment '?='. Default is False.
        position(int): A position in the input string where attribute is
            defined.
    """
    def __init__(self, name, cls=None, mult=MULT_ONE, cont=True, ref=False,
                 bool_assignment=False, position=0):
        self.name = name
        self.cls = cls
        self.mult = mult
        self.cont = cont
        self.ref = ref
        self.bool_assignment = bool_assignment
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
            {clsname: cls} that holds meta-classes imported from the given
            grammar file. Special key 'base' is used for BASETYPE classes.
            None key is used for all classes imported from the grammar
            given as a string.
        namespace_stack(list): A stack of namespace names (usually absolute
            filenames). Used to keep track of the current namespace.
        imported_namespaces(dict): A dict from namespace name to the list of
            references to imported namespaces. Used in searches for the
            unqualified rules.
        builtins(dict): A dict of named object used in linking phase.
            References to named objects not defined in the model will be
            searched here.
        classes(dict): A dict of user supplied classes to use instead of
            generic ones.
        obj_processors(dict): A dict of user supplied object processors.
    """

    def __init__(self, file_name=None, classes=None, builtins=None,
                 auto_init_attributes=True, ignore_case=False,
                 skipws=True, ws=None, autokwd=False, debug=False):
        """
        Args:
            file_name(str): A file name if meta-model is going to be
                constructed from file or None otherwise.
            classes(dict of python classes): Custom meta-classes used
                instead of generic ones.
            builtins(dict of named objects): Named objects used in linking
                phase. This objects are part of each model.
            auto_init_attributes(bool): If set than model attributes will be
                automatically initialized to non-None values (e.g. for INT
                attribute value will be 0, for BOOL it will be False). If this
                parameter is False than all attributes will have a value
                of None if not defined in the model. The only exception is
                bool assignment ('?=') which always have a default of False.
                Default is True.
            ignore_case(bool): If case is ignored (default=False)
            skipws (bool): Should the whitespace skipping be done.
                Default is True.
            ws (str): A string consisting of whitespace characters.
            autokwd(bool): If keyword-like matches should be matched on word
                boundaries. Default is False.
            debug(bool): Should debug messages be printed.
        """

        self.file_name = file_name
        self.rootcls = None

        self.builtins = builtins

        # Convert classes to dict for easier lookup
        self.user_classes = {}
        if classes:
            for c in classes:
                self.user_classes[c.__name__] = c

        self.debug = debug
        self.auto_init_attributes = auto_init_attributes
        self.ignore_case = ignore_case
        self.skipws = skipws
        self.ws = ws
        self.autokwd = autokwd

        # Registered model processors
        self._model_processors = []

        # Registered object processors
        self.obj_processors = {}

        # Namespaces
        self.namespaces = {}
        self.namespace_stack = []

        # Imported namespaces
        self.imported_namespaces = {}

        # Create new namespace for BASETYPE classes
        self._enter_namespace('base')

        # Base types hierarchy should exist in each meta-model
        base_id = self.new_class('ID', ID, 0)
        base_string = self.new_class('STRING', STRING, 0)
        base_bool = self.new_class('BOOL', BOOL, 0)
        base_int = self.new_class('INT', INT, 0)
        base_float = self.new_class('FLOAT', FLOAT, 0)
        base_number = self.new_class('NUMBER', NUMBER, 0,
                                     [base_float, base_int])
        self.new_class('BASETYPE', BASETYPE, 0,
                       [base_number, base_id, base_string, base_bool])

        # If file_name is given its absolute path will be a namespace
        if file_name:
            file_name = os.path.abspath(file_name)

        # Enter namespace for given file or None if metamodel is
        # constructed from string.
        self._enter_namespace(file_name)

    def _enter_namespace(self, namespace_name):
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

    def _leave_namespace(self):
        """
        Leaves current namespace (i.e. grammar file).
        """
        self.namespace_stack.pop()

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

    def set_rule(self, name, rule):
        """
        For the given rule/class name sets PEG rule.
        """
        self[name]._peg_rule = rule

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
            self._enter_namespace(import_file_name)
            metamodel_from_file(import_file_name, metamodel=self)
            self._leave_namespace()

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
                _peg_rule(ParsingExpression): An arpeggio PEG rule that matches
                    this class.
            """
            # Attribute information (MetaAttr instances) keyed by name.
            _attrs = OrderedDict()

            # A list of inheriting classes
            _inh_by = inherits if inherits else []

            _position = position

            # The type of the rule this meta-class results from.
            # There are three rule types: normal, abstract and match
            _type = RULE_NORMAL

            _peg_rule = peg_rule

            def __init__(self):
                """
                Initializes attributes.
                """
                # For generic meta-class instantiation
                # call default attribute initializers.
                self.init_attrs(self, self._attrs)

            @staticmethod
            def init_attrs(obj, attrs):
                """
                Initialize obj attributes.
                Args:
                    obj(object): A python object to set attributes to.
                    attrs(dict): A dict of meta-attributes from meta-class.
                """
                for attr in attrs.values():
                    if attr.mult in [MULT_ZEROORMORE, MULT_ONEORMORE]:
                        # list
                        setattr(obj, attr.name, [])
                    elif attr.cls.__name__ in BASE_TYPE_NAMES:
                        # Instantiate base python type
                        if self.auto_init_attributes:
                            setattr(obj, attr.name,
                                    python_type(attr.cls.__name__)())
                        else:
                            # See https://github.com/igordejanovic/textX/issues/11
                            if attr.bool_assignment:
                                # Only ?= assignments shall have default
                                # value of False.
                                setattr(obj, attr.name, False)
                            else:
                                # Set base type attribute to None initially
                                # in order to be able to detect if an optional
                                # values are given in the model. Default values
                                # can be specified using object processors.
                                setattr(obj, attr.name, None)
                    else:
                        # Reference to other obj
                        setattr(obj, attr.name, None)

            @classmethod
            def new_attr(clazz, name, cls=None, mult=MULT_ONE, cont=True,
                         ref=False, bool_assignment=False, position=0):
                """Creates new meta attribute of this class."""
                attr = MetaAttr(name, cls, mult, cont, ref, bool_assignment,
                                position)
                clazz._attrs[name] = attr
                return attr

        cls = Meta
        cls.__name__ = name
        cls._metamodel = self

        cls._typename = cls.__name__

        # Push this class and PEG rule in the current namespace
        current_namespace = self.namespaces[self.namespace_stack[-1]]
        current_namespace[name] = cls

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
                # yield class
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

    def model_from_str(self, model_str):
        """
        Instantiates model from the given string.
        """
        model = self.parser.get_model_from_str(model_str)
        for p in self._model_processors:
            p(model, self)
        return model

    def model_from_file(self, file_name, encoding='utf-8'):
        """
        Instantiates model from the given file.
        """
        model = self.parser.get_model_from_file(file_name, encoding)
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

    def register_obj_processors(self, obj_processors):
        """
        Object processors are callables that will be called after
        each successful model object construction.
        Those callables receive model object as its parameter.
        Registration of new object processors will replace previous.

        Args:
            obj_processors(dict): A dictionary where key=class name,
                value=callable
        """
        self.obj_processors = obj_processors


def metamodel_from_str(lang_desc, metamodel=None, **kwargs):
    """
    Creates a new metamodel from the textX description given as a string.

    Args:
        lang_desc(str): A textX language description.
        metamodel(TextXMetaModel): A metamodel that should be used.
        other params: See TextXMetaModel.

    """
    if not metamodel:
        metamodel = TextXMetaModel(**kwargs)

    language_from_str(lang_desc, metamodel)

    return metamodel


def metamodel_from_file(file_name, **kwargs):
    """
    Creates new metamodel from the given file.

    Args:
        file_name(str): The name of the file with textX language description.
        other params: See metamodel_from_str.
    """
    with codecs.open(file_name, 'r', 'utf-8') as f:
        lang_desc = f.read()

    metamodel = metamodel_from_str(lang_desc=lang_desc,
                                   file_name=file_name, **kwargs)

    return metamodel
