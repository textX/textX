#######################################################################
# Name: metamodel.py
# Purpose: Meta-model construction.
# Author: Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# Copyright: (c) 2014-2017 Igor R. Dejanovic <igor DOT dejanovic AT gmail DOT com>
# License: MIT License
#######################################################################

import codecs
import os
from collections import OrderedDict
from arpeggio import DebugPrinter
from .textx import language_from_str, python_type, BASE_TYPE_NAMES, ID, BOOL,\
    INT, FLOAT, STRING, NUMBER, BASETYPE, OBJECT
from .const import MULT_ONE, MULT_ZEROORMORE, MULT_ONEORMORE, RULE_MATCH, \
    RULE_ABSTRACT


__all__ = ['metamodel_from_str', 'metamodel_from_file']


BASE_FILTERS = {
    'BOOL': lambda x: x == '1' or x.lower() == 'true',
    'INT': lambda x: int(x),
    'FLOAT': lambda x: float(x),
    'STRING': lambda x: x[1:-1].replace(r'\"', r'"').replace(r"\'", "'")
}


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


class TextXMetaModel(DebugPrinter):
    """
    Meta-model contains all information about language abstract syntax.
    Furthermore, this class is in charge for model instantiation and new
    language class creation. This class should not be instantiated by the user
    directly. It's instantiated by the metamodel_from_(file/str) functions.

    Attributes:
        file_name(str): A file name if meta-model is going to be
            constructed from file or None otherwise.
        auto_init_attributes(bool): If set then model attributes will be
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
        memoization(bool): If memoization should be used (a.k.a. packrat
            parsing). Default is False.
        debug(bool): Should debug messages be printed.
        builtins(dict): A dict of named object used in linking phase.
            References to named objects not defined in the model will be
            searched here.
        classes(list of classes): A list of user supplied classes to use
            instead of the dynamically created.
        match_filters(dict of callables): Callables keyed by match rule names
            used to transform strings matched by match rules.
        obj_processors(dict): A dict of user supplied object processors keyed
            by rule/class name (may be a fully qualified name).
        rootcls(TextXClass): A language class that is a root of the metamodel.
        root_path(str): The root dir used for the import statement.
        namespaces(dict): A mapping from fully qualified module names to dicts
            in the form {clsname: cls} that holds meta-classes imported from
            the given grammar file. Special key '__base__' is used for BASETYPE
            classes. None key is used for all classes imported from the grammar
            given as a string.
        _namespace_stack(list): A stack of namespace names (fully qualified
            module names). Used to keep track of the current namespace.
        _imported_namespaces(dict): A mapping from namespace name to the list
            of references to imported namespaces. Used in searches for
            unqualified rules.
    """

    def __init__(self, file_name=None, classes=None, builtins=None,
                 match_filters=None, auto_init_attributes=True,
                 ignore_case=False, skipws=True, ws=None, autokwd=False,
                 memoization=False, **kwargs):
        super(TextXMetaModel, self).__init__(**kwargs)

        self.file_name = file_name
        self.rootcls = None

        self.builtins = builtins

        # Convert classes to dict for easier lookup
        self.user_classes = {}
        if classes:
            for c in classes:
                self.user_classes[c.__name__] = c

        self.match_filters = match_filters if match_filters else {}

        self.auto_init_attributes = auto_init_attributes
        self.ignore_case = ignore_case
        self.skipws = skipws
        self.ws = ws
        self.autokwd = autokwd
        self.memoization = memoization

        # Registered model processors
        self._model_processors = []

        # Registered object processors
        self.obj_processors = {}

        # Namespaces
        self.namespaces = {}
        self._namespace_stack = []

        # Imported namespaces
        self._imported_namespaces = {}

        # Create new namespace for BASETYPE classes
        self._enter_namespace('__base__')

        # Base types hierarchy should exist in each meta-model
        base_id = self._new_class('ID', ID, 0)
        base_string = self._new_class('STRING', STRING, 0)
        base_bool = self._new_class('BOOL', BOOL, 0)
        base_int = self._new_class('INT', INT, 0)
        base_float = self._new_class('FLOAT', FLOAT, 0)
        base_number = self._new_class('NUMBER', NUMBER, 0,
                                      inherits=[base_float, base_int])
        base_type = self._new_class('BASETYPE', BASETYPE, 0,
                                    inherits=[base_number, base_bool, base_id,
                                              base_string])
        self._new_class('OBJECT', OBJECT, 0, inherits=[base_type],
                        rule_type=RULE_ABSTRACT)

        # Resolve file name to absolute path.
        if file_name:
            file_name = os.path.abspath(file_name)

        # Root path will be dir name of the file if loaded from file.
        # If the grammar is not loaded from file 'import' statement can't be
        # used.
        self.root_path = os.path.dirname(file_name) if file_name else None

        # Enter namespace for given file or None if metamodel is
        # constructed from string.
        self._enter_namespace(self._namespace_for_file_name(file_name))

    def _namespace_for_file_name(self, file_name):
        if file_name is None or self.root_path is None:
            return None
        file_name = os.path.abspath(file_name)
        p = os.path
        q = p.splitext(p.relpath(file_name, start=self.root_path))[0]
        return '.'.join(p.split(q)[1:])

    def _enter_namespace(self, namespace_name):
        """
        A namespace is usually an absolute file name of the grammar.
        A special namespace '__base__' is used for BASETYPE namespace.
        """
        if namespace_name not in self.namespaces:
            self.namespaces[namespace_name] = {}

            # BASETYPE namespace is imported in each namespace
            # as the first namespace to be searched.
            self._imported_namespaces[namespace_name] = \
                [self.namespaces['__base__']]

        self._namespace_stack.append(namespace_name)

    def _leave_namespace(self):
        """
        Leaves current namespace (i.e. grammar file).
        """
        self._namespace_stack.pop()

    def _new_import(self, import_name):
        """
        Starts a new import.
        Args:
            import_name(str): A relative import in the dot syntax
                (e.g. "first.second.expressions")
        """

        # Import can't be used if meta-model is loaded from string
        assert self.root_path is not None, \
            '"import" statement can not be used if meta-model is ' \
            'loaded from string.'

        # Find the absolute file name of the import based on the relative
        # import_name and current namespace
        current_namespace = self._namespace_stack[-1]
        if '.' in current_namespace:
            root_namespace = current_namespace.rsplit('.', 1)[0]
            import_name = "%s.%s" % (root_namespace, import_name)

        import_file_name = "%s.tx" % os.path.join(self.root_path,
                                                  *import_name.split("."))

        if import_name not in self.namespaces:
            self._enter_namespace(import_name)
            if self.debug:
                self.dprint("*** IMPORTING FILE: %s" % import_file_name)
            metamodel_from_file(import_file_name, metamodel=self)
            self._leave_namespace()

        # Add the import to the imported_namespaces for current namespace
        # so that resolving of current grammar searches imported grammars
        # in the order of import
        self._imported_namespaces[current_namespace].append(
            self.namespaces[import_name])

    def _new_class(self, name, peg_rule, position, position_end=None,
                   inherits=None, root=False, rule_type=RULE_MATCH):
        """
        Creates a new class with the given name in the current namespace.
        Args:
            name(str): The name of the class.
            peg_rule(ParserExpression): An arpeggio peg rule used to match
                this class.
            positon(int): A position in the input where class is defined.
            root(bool): Is this class a root class of the metamodel.
            rule_type: The type of the rule this meta-class is for. One of
                RULE_COMMON, RULE_ABSTRACT or RULE_MATCH.
        """

        class Meta(TextXClass):
            """
            Dynamic metaclass. Each textX rule will result in creating
            one Meta class with the type name of the rule.
            Model is a graph of python instances of this metaclasses.
            Attributes:
                _tx_attrs(dict): A dict of meta-attributes keyed by name.
                    Used by common rules.
                _tx_inh_by(list): Classes that inherits this one. Used by
                    abstract rules.
                _tx_position(int): A position in the input string where this
                    class is defined.
                _tx_position_end(int): A position in the input string where
                    this class ends.
                _tx_type(int): The type of the textX rule this class is created
                    for. See textx.const
                _tx_metamodel(TextXMetaModel): A metamodel this class belongs
                    to.
                _tx_peg_rule(ParsingExpression): An Arpeggio PEG rule that
                    matches this class.
            """

            def __repr__(self):
                if hasattr(self, 'name'):
                    return "<{}:{}>".format(name, self.name)
                else:
                    return "<textx:{} object at {}>"\
                        .format(name, hex(id(self)))

        cls = Meta
        cls.__name__ = name

        self._init_class(cls, peg_rule, position, position_end, inherits, root,
                         rule_type)

        return cls

    def _init_class(self, cls, peg_rule, position, position_end=None,
                    inherits=None, root=False, rule_type=RULE_MATCH):
        """
        Setup meta-class special attributes, namespaces etc. This is called
        both for textX created classes as well as user classes.
        """
        cls._tx_metamodel = self

        # Attribute information (MetaAttr instances) keyed by name.
        cls._tx_attrs = OrderedDict()

        # A list of inheriting classes
        cls._tx_inh_by = inherits if inherits else []

        cls._tx_position = position

        cls._tx_position_end = \
            position if position_end is None else position_end

        # The type of the rule this meta-class results from.
        # There are three rule types: common, abstract and match
        # Base types are match rules.
        cls._tx_type = rule_type

        cls._tx_peg_rule = peg_rule
        if peg_rule:
            peg_rule._tx_class = cls

        # Push this class and PEG rule in the current namespace
        current_namespace = self.namespaces[self._namespace_stack[-1]]
        current_namespace[cls.__name__] = cls

        if root:
            self.rootcls = cls

    def _init_obj_attrs(self, obj, user=False):
        """
        Initialize obj attributes.
        Args:
            obj(object): A python object to set attributes to.
            user(bool): If this object is a user object mangle attribute names.
        """
        for attr in obj.__class__._tx_attrs.values():

            if user:
                # Mangle name to prvent name clashing
                attr_name = "_txa_%s" % attr.name
            else:
                attr_name = attr.name

            if attr.mult in [MULT_ZEROORMORE, MULT_ONEORMORE]:
                # list
                setattr(obj, attr_name, [])
            elif attr.cls.__name__ in BASE_TYPE_NAMES:
                # Instantiate base python type
                if self.auto_init_attributes:
                    setattr(obj, attr_name,
                            python_type(attr.cls.__name__)())
                else:
                    # See https://github.com/igordejanovic/textX/issues/11
                    if attr.bool_assignment:
                        # Only ?= assignments shall have default
                        # value of False.
                        setattr(obj, attr_name, False)
                    else:
                        # Set base type attribute to None initially
                        # in order to be able to detect if an optional
                        # values are given in the model. Default values
                        # can be specified using object processors.
                        setattr(obj, attr_name, None)
            else:
                # Reference to other obj
                setattr(obj, attr_name, None)

    def _new_cls_attr(self, clazz, name, cls=None, mult=MULT_ONE, cont=True,
                      ref=False, bool_assignment=False, position=0):
        """Creates new meta attribute of this class."""
        attr = MetaAttr(name, cls, mult, cont, ref, bool_assignment,
                        position)
        clazz._tx_attrs[name] = attr
        return attr

    def validate(self):
        """
        Validates metamodel. Called after construction to check for some
        textX rules.
        """
        # TODO: Implement complex textX validations.

    def convert(self, value, _type):
        """
        Convert instances of textx types and rules to python base types and
        user types using registered match filters.
        """
        return self.match_filters.get(
            _type,
            BASE_FILTERS.get(_type, lambda x: x)
        )(value)

    def __getitem__(self, name):
        """
        Search for and return class and peg_rule with the given name.
        Returns:
            TextXClass, ParsingExpression
        """
        if "." in name:
            # Name is fully qualified
            namespace, name = name.rsplit('.', 1)
            return self.namespaces[namespace][name]
        else:
            # If not fully qualified search in the current namespace
            # and after that in the imported_namespaces
            if name in self._current_namespace:
                return self._current_namespace[name]

            for namespace in \
                    self._imported_namespaces[self._namespace_stack[-1]]:
                if name in namespace:
                    return namespace[name]

            raise KeyError("{} metaclass does not exists in the metamodel "
                           .format(name))

    def __iter__(self):
        """
        Iterate over all classes in the current namespace and imported
        namespaces.
        """

        # Current namespace
        for name in self._current_namespace:
            yield self._current_namespace[name]

        # Imported namespaces
        for namespace in \
                self._imported_namespaces[self._namespace_stack[-1]]:
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
    def _current_namespace(self):
        return self.namespaces[self._namespace_stack[-1]]

    def model_from_str(self, model_str, debug=None):
        """
        Instantiates model from the given string.
        """
        model = self.parser.get_model_from_str(model_str, debug=debug)
        for p in self._model_processors:
            p(model, self)
        return model

    def model_from_file(self, file_name, encoding='utf-8', debug=None):
        """
        Instantiates model from the given file.
        """
        model = self.parser.get_model_from_file(file_name,
                                                encoding, debug=debug)
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
