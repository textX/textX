"""
Meta-model construction.
"""
import codecs
import os
import warnings
from collections import OrderedDict
from os.path import abspath, dirname, join

from arpeggio import DebugPrinter

from textx.const import (
    MULT_ONE,
    MULT_ONEORMORE,
    MULT_ZEROORMORE,
    RULE_ABSTRACT,
    RULE_MATCH,
)
from textx.exceptions import TextXError
from textx.lang import (
    BASE_TYPE_NAMES,
    BASETYPE,
    BOOL,
    FLOAT,
    ID,
    INT,
    NUMBER,
    OBJECT,
    STRICTFLOAT,
    STRING,
    language_from_str,
    python_type,
)
from textx.scoping.rrel import create_rrel_scope_provider

from .model_params import ModelParamDefinitions, ModelParams
from .registration import LanguageDesc, metamodel_for_language

__all__ = ["metamodel_from_str", "metamodel_from_file"]


def metamodel_from_str(lang_desc, metamodel=None, **kwargs):
    """
    Creates a new metamodel from the textX description given as a string.

    Args:
        lang_desc(str): A textX language description.
        metamodel(TextXMetaModel): A metamodel that should be used.
        other params: See TextXMetaModel.

    """

    is_main_metamodel = metamodel is None

    if not metamodel:
        metamodel = TextXMetaModel(**kwargs)

    file_name = kwargs.get("file_name")

    language_from_str(lang_desc, metamodel, file_name)

    if is_main_metamodel:
        metamodel.validate_user_classes()

    return metamodel


def metamodel_from_file(file_name, **kwargs):
    """
    Creates new metamodel from the given file.

    Args:
        file_name(str): The name of the file with textX language description.
        other params: See metamodel_from_str.
    """
    with codecs.open(file_name, "r", "utf-8") as f:
        lang_desc = f.read()

    metamodel = metamodel_from_str(lang_desc=lang_desc, file_name=file_name, **kwargs)

    return metamodel


class MetaAttr:
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

    def __init__(
        self,
        name,
        cls=None,
        mult=MULT_ONE,
        cont=True,
        ref=False,
        bool_assignment=False,
        position=0,
    ):
        self.name = name
        self.cls = cls
        self.mult = mult
        self.cont = cont
        self.ref = ref
        self.bool_assignment = bool_assignment
        self.position = position

    def __eq__(self, other):
        return self.name == other.name \
            and self.cls == other.cls \
            and self.mult == other.mult \
            and self.cont == other.cont \
            and self.ref == other.ref \
            and self.bool_assignment == other.bool_assignment


class TextXMetaClass(type):
    """
    A meta-class for all textX generated classes.
    """
    def __repr__(cls):
        return f"<textx:{cls._tx_fqn} class at {id(cls)}>"



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
        textx_tools_support(bool): If True, additional properties will be
            added to model. Default is False.
        debug(bool): Should debug messages be printed.
        builtins(dict): A dict of named object used in linking phase.
            References to named objects not defined in the model will be
            searched here.
        builtin_models(ModelRepository): An optional repository of preloaded models
            to be used during reference resolving. These models will be searched
            as a fallback before `builtins`.
        classes(list of classes or callable): A list of user supplied classes
            to use instead of the dynamically created or a callable providing
            those classes. The callable must accept a rule name and return a
            class for that rule name or None.
        _obj_processors(dict): A dict of user supplied object processors keyed
            by rule/class name (may be a fully qualified name).
        rootcls(TextXClass): A language class that is a root of the meta-model.
        root_path(str): The root dir used for the import statement.
        namespaces(dict): A mapping from fully qualified module names to dicts
            in the form `{clsname: cls}` that holds meta-classes imported from
            the given grammar file. If `clsname` is a special key `__aliases__`
            it maps to the dict of `{alias: language}` mappings for the
            current grammar file. It is used for a fully qualified resolving of
            references. A special key '__base__' is used for BASETYPE
            classes. `None` key is used for all classes imported from the
            grammar given as a string.
        _namespace_stack(list): A stack of namespace names (fully qualified
            module names). Used to keep track of the current namespace.
        _imported_namespaces(dict): A mapping from namespace name to the list
            of references to imported namespaces. Used in searches for
            unqualified rules.
        _tx_model_repository: optional global repository. Normally such
            objects are owned by models only. However, if the models shall
            interact globally (which means if two separately loaded models
            should interact), this attribute must be set via an optional
            constructor parameter "global_repository=True" or
            "global_repository=GlobalModelRepository()".
        use_regexp_group (bool): if True, regexp terminals are
            replaced with the group value, if they have exactly one group.
    """

    def __init__(
        self,
        file_name=None,
        classes=None,
        builtins=None,
        builtin_models=None,
        auto_init_attributes=True,
        ignore_case=False,
        skipws=True,
        ws=None,
        autokwd=False,
        memoization=False,
        textx_tools_support=False,
        use_regexp_group=False,
        **kwargs,
    ):
        # evaluate optional parameter "global_repository"
        global_repository = kwargs.pop("global_repository", False)
        if global_repository:
            from textx.scoping import GlobalModelRepository

            if isinstance(global_repository, GlobalModelRepository):
                self._tx_model_repository = global_repository
            else:
                self._tx_model_repository = GlobalModelRepository()

        super().__init__(**kwargs)

        self.model_param_defs = ModelParamDefinitions()
        self.model_param_defs.add("project_root", "the project root path")

        self.file_name = file_name
        self.rootcls = None

        self.builtins = builtins
        self.builtin_models = builtin_models

        # Convert classes to dict for easier lookup
        self.user_classes = {}
        self.user_classes_provider = None
        self._used_rule_names_for_user_classes = set()
        if classes:
            if callable(classes):
                self.user_classes_provider = classes
            else:
                for c in classes:
                    self.user_classes[c.__name__] = c

        self.auto_init_attributes = auto_init_attributes
        self.ignore_case = ignore_case
        self.skipws = skipws
        self.ws = ws
        self.autokwd = autokwd
        self.memoization = memoization
        self.textx_tools_support = textx_tools_support
        self.use_regexp_group = use_regexp_group

        # Registered model processors
        self._model_processors = []

        # Match rule and base type conversion callables
        self._default_obj_processors = {
            "BOOL": lambda x: x == "1" or x.lower() == "true",
            "INT": lambda x: int(x),
            "FLOAT": lambda x: float(x),
            "STRICTFLOAT": lambda x: float(x),
            "STRING": lambda x: x[1:-1].replace(r"\"", r'"').replace(r"\'", "'"),
        }

        # Registered object processors (use _default_obj_processors)
        self.register_obj_processors({})

        # Registered scope provider
        self.scope_providers = {}

        # Namespaces
        self.namespaces = {}
        self._namespace_stack = []

        # Imported namespaces
        self._imported_namespaces = {}

        # Referenced languages
        self.referenced_languages = {}

        # Create new namespace for BASETYPE classes
        self._enter_namespace("__base__")

        # Base types hierarchy should exist in each meta-model
        base_id = self._new_class("ID", ID, 0)
        base_string = self._new_class("STRING", STRING, 0)
        base_bool = self._new_class("BOOL", BOOL, 0)
        base_int = self._new_class("INT", INT, 0)
        base_float = self._new_class("FLOAT", FLOAT, 0)
        base_strictfloat = self._new_class("STRICTFLOAT", STRICTFLOAT, 0)
        base_number = self._new_class(
            "NUMBER", NUMBER, 0, inherits=[base_strictfloat, base_int]
        )
        base_type = self._new_class(
            "BASETYPE",
            BASETYPE,
            0,
            inherits=[base_number, base_float, base_bool, base_id, base_string],
        )
        self._new_class(
            "OBJECT", OBJECT, 0, inherits=[base_type], rule_type=RULE_ABSTRACT
        )

        self._leave_namespace()

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

    def register_scope_providers(self, sp):
        self.scope_providers = sp
        for k, v in self.scope_providers.items():
            if isinstance(v, str):
                self.scope_providers[k] = create_rrel_scope_provider(v)

    def _namespace_for_file_name(self, file_name):
        if file_name is None or self.root_path is None:
            return None
        file_name = os.path.abspath(file_name)
        p = os.path
        q = p.splitext(p.relpath(file_name, start=self.root_path))[0]
        return ".".join(p.split(q)[1:])

    def _enter_namespace(self, namespace_name):
        """
        A namespace is usually an absolute file name of the grammar.
        A special namespace '__base__' is used for BASETYPE namespace.
        """
        if namespace_name not in self.namespaces:
            self.namespaces[namespace_name] = {}

            # BASETYPE namespace is imported in each namespace
            # as the first namespace to be searched.
            self._imported_namespaces[namespace_name] = [self.namespaces["__base__"]]

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
        assert self.root_path is not None, (
            '"import" statement can not be used if meta-model is ' "loaded from string."
        )

        # Find the absolute file name of the import based on the relative
        # import_name and current namespace
        current_namespace = self._namespace_stack[-1]
        if "." in current_namespace:
            root_namespace = current_namespace.rsplit(".", 1)[0]
            import_name = f"{root_namespace}.{import_name}"

        import_file_name = "{}.tx".format(
            os.path.join(self.root_path, *import_name.split(".")))

        if import_name not in self.namespaces:
            self._enter_namespace(import_name)
            if self.debug:
                self.dprint(f"*** IMPORTING FILE: {import_file_name}")
            metamodel_from_file(import_file_name, metamodel=self)
            self._leave_namespace()

        # Add the import to the imported_namespaces for current namespace
        # so that resolving of current grammar searches imported grammars
        # in the order of import
        self._imported_namespaces[current_namespace].append(self.namespaces[import_name])


    def _new_class(
        self,
        name,
        peg_rule,
        position,
        position_end=None,
        inherits=None,
        root=False,
        rule_type=RULE_MATCH,
    ):
        """
        Creates a new class with the given name in the current namespace.
        Args:
            name(str): The name of the class.
            peg_rule(ParserExpression): An arpeggio peg rule used to match
                this class.
            position(int): A position in the input where class is defined.
            root(bool): Is this class a root class of the metamodel.
            rule_type: The type of the rule this meta-class is for. One of
                RULE_COMMON, RULE_ABSTRACT or RULE_MATCH.
        """

        class TextXClass(metaclass=TextXMetaClass):
            """
            Dynamically created class. Each textX rule will result in
            creating one Python class with the type name of the rule.
            textX model is a graph of instances of these Python classes.

            Attributes:
                _tx_attrs(dict): A dict of meta-attributes keyed by name.
                    Used by common rules.
                _tx_inh_by(list): Classes that inherits this one. Used by
                    abstract rules.
                _tx_position(int): A position in the input string where
                    this class is defined.
                _tx_position_end(int): A position in the input string where
                    this class ends.
                _tx_type(int): The type of the textX rule this class is
                    created for. See textx.const
                _tx_metamodel(TextXMetaModel): A metamodel this class
                    belongs to.
                _tx_peg_rule(ParsingExpression): An Arpeggio PEG rule that
                    matches this class.

            """

            def __repr__(self):
                """
                Used for TextXClass bellow.
                """
                if hasattr(self, "name"):
                    return f"<{name}:{self.name}>"
                else:
                    return f"<textx:{self._tx_fqn} instance at {hex(id(self))}>"

        cls = TextXClass
        cls.__name__ = name

        self._init_class(cls, peg_rule, position, position_end, inherits, root, rule_type)

        return cls


    def _init_class(
        self,
        cls,
        peg_rule,
        position,
        position_end=None,
        inherits=None,
        root=False,
        rule_type=RULE_MATCH,
        external_attributes=False,
    ):
        """
        Setup meta-class special attributes, namespaces etc. This is called
        both for textX created classes as well as user classes.
        """
        cls._tx_metamodel = self
        cls._tx_filename = self.file_name

        # Attribute information (MetaAttr instances) keyed by name.
        cls._tx_attrs = OrderedDict()

        # A list of inheriting classes
        cls._tx_inh_by = inherits if inherits else []

        cls._tx_position = position

        cls._tx_position_end = position if position_end is None else position_end

        # The type of the rule this meta-class results from.
        # There are three rule types: common, abstract and match
        # Base types are match rules.
        cls._tx_type = rule_type

        cls._tx_peg_rule = peg_rule
        if peg_rule:
            peg_rule._tx_class = cls

        # Push this class and PEG rule in the current namespace
        current_namespace = self.namespaces[self._namespace_stack[-1]]
        cls._tx_fqn = self._cls_fqn(cls)
        current_namespace[cls.__name__] = cls

        if root:
            self.rootcls = cls

        if external_attributes:
            cls._tx_obj_attrs = {}

    def _cls_fqn(self, cls):
        """
        Returns fully qualified name for the class based on current namespace
        and the class name.
        """
        ns = self._namespace_stack[-1]
        if ns in ["__base__", None]:
            return cls.__name__
        else:
            return ns + "." + cls.__name__

    def _init_obj_attrs(self, obj):
        """
        Initialize obj attributes.
        Args:
            obj(object): A python object to set attributes to.
        """
        for attr in obj.__class__._tx_attrs.values():
            if attr.mult in [MULT_ZEROORMORE, MULT_ONEORMORE]:
                # list
                setattr(obj, attr.name, [])
            elif attr.cls.__name__ in BASE_TYPE_NAMES:
                # Instantiate base python type
                if self.auto_init_attributes:
                    setattr(obj, attr.name, python_type(attr.cls.__name__)())
                else:
                    # See https://github.com/textX/textX/issues/11
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

    def _new_cls_attr(
        self,
        clazz,
        name,
        cls=None,
        mult=MULT_ONE,
        cont=True,
        ref=False,
        bool_assignment=False,
        position=0,
    ):
        """Creates new meta attribute of this class."""
        attr = MetaAttr(name, cls, mult, cont, ref, bool_assignment, position)
        clazz._tx_attrs[name] = attr
        return attr

    def has_obj_processor(self, _type):
        return _type in self._obj_processors

    def process(self, value, _type, filename, col, line, nchar=None):
        """
        Process a value with the given type
        Convert instances of textx types and match rules to python types.

        Args:
            value: the value
            _type: the type of the value (TextX Class)
            filename: filename for current object
            col: col for current object
            line: line for current object
            nchar: character count for current object (default: None)
        Returns:
            None or a value used by TextX to replace the object during
            model creation.
        """
        try:
            return self._obj_processors.get(_type, lambda x: x)(value)
        except Exception as e:
            from textx.exceptions import TextXError

            if isinstance(e, TextXError):
                if e.col is None:
                    e.col = col
                if e.line is None:
                    e.line = line
                if e.filename is None:
                    e.filename = filename
                raise e
            else:
                raise

    def validate(self):
        """
        Validates metamodel. Called after construction to check for some
        textX rules.
        """
        # TODO: Implement complex textX validations.
        pass

    def validate_user_classes(self):
        """
        Validates user classes of the meta model.
        Called after construction of the main metamodel (not
        imported ones).
        """
        from textx.exceptions import TextXSemanticError

        for user_class in self.user_classes.values():
            if user_class.__name__ not in self._used_rule_names_for_user_classes:
                # It is not a user class used in the grammar
                raise TextXSemanticError(
                    f"{user_class.__name__} class is not used in the grammar"
                )

    def __getitem__(self, name):
        """
        Search for and return class and peg_rule with the given name.
        Returns:
            TextXClass, ParsingExpression
        """
        if "." in name:
            # Name is fully qualified
            namespace, name = name.rsplit(".", 1)
            if namespace in self.referenced_languages:
                language = self.referenced_languages[namespace]
                referenced_metamodel = metamodel_for_language(language)
                return referenced_metamodel[name]
            else:
                return self.namespaces[namespace][name]
        else:
            # If not fully qualified search in the current namespace
            # and after that in the imported_namespaces
            if name in self._current_namespace:
                return self._current_namespace[name]

            for namespace in self._imported_namespaces[self._namespace_stack[-1]]:
                if name in namespace:
                    return namespace[name]

            raise KeyError(f"{name} metaclass does not exists in the meta-model ")

    def __iter__(self):
        """
        Iterate over all classes in the current namespace and imported
        namespaces.
        """

        # Current namespace
        for name in self._current_namespace:
            yield self._current_namespace[name]

        # Imported namespaces
        for namespace in self._imported_namespaces[self._namespace_stack[-1]]:
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

    def model_from_str(
        self,
        model_str,
        file_name=None,
        debug=None,
        pre_ref_resolution_callback=None,
        encoding="utf-8",
        **kwargs,
    ):
        """
        Instantiates model from the given string.
        :param pre_ref_resolution_callback: called before references are
               resolved. This can be useful to manage models distributed
               across files (scoping)
        :param **kwargs additional arguments available through
                _tx_model_params after initiating the model. The attribute
                is set while executing pre_ref_resolution_callback (see
                scoping.md)
        """
        self.model_param_defs.check_params("from_str", **kwargs)

        if not isinstance(model_str, str):
            raise TextXError("textX accepts only strings.")

        if file_name is None:

            def kwargs_callback(other_model):
                if hasattr(other_model, "_tx_metamodel"):
                    other_model._tx_model_params = ModelParams(kwargs)
                if pre_ref_resolution_callback:
                    pre_ref_resolution_callback(other_model)

            model = self._parser_blueprint.clone().get_model_from_str(
                model_str, debug=debug, pre_ref_resolution_callback=kwargs_callback
            )

            for p in self._model_processors:
                p(model, self)
        else:
            model = self.internal_model_from_file(
                file_name,
                encoding,
                debug,
                model_str=model_str,
                pre_ref_resolution_callback=pre_ref_resolution_callback,
                model_params=ModelParams(kwargs),
            )

        return model

    def model_from_file(self, file_name, encoding="utf-8", debug=None, **kwargs):
        self.model_param_defs.check_params(file_name, **kwargs)

        return self.internal_model_from_file(
            file_name, encoding, debug, model_params=ModelParams(kwargs)
        )

    def internal_model_from_file(
        self,
        file_name,
        encoding="utf-8",
        debug=None,
        pre_ref_resolution_callback=None,
        is_main_model=True,
        model_str=None,
        model_params=None,
    ):
        """
        Instantiates model from the given file.
        :param pre_ref_resolution_callback: called before references are
               resolved. This can be useful to manage models distributed
               across files (scoping)
        """
        assert model_params is not None, "model_params are required in all cases"
        file_name = abspath(file_name)
        model = None
        callback = pre_ref_resolution_callback

        if hasattr(self, "_tx_model_repository"):
            # metamodel has a global repo
            if not callback:

                def _pre_ref_resolution_callback(other_model):
                    from textx.scoping import GlobalModelRepository

                    filename = other_model._tx_filename
                    assert filename
                    # print("METAMODEL PRE-CALLBACK => {}".format(filename))
                    other_model._tx_model_repository = GlobalModelRepository(
                        self._tx_model_repository.all_models
                    )
                    self._tx_model_repository.all_models[filename] = other_model

                callback = _pre_ref_resolution_callback
            if self._tx_model_repository.all_models.has_model(file_name):
                model = self._tx_model_repository.all_models[file_name]

        def kwargs_callback(other_model):
            if hasattr(other_model, "_tx_metamodel"):
                other_model._tx_model_params = model_params
            if callback:
                callback(other_model)

        if not model:
            # Read model from file
            if not model_str:
                with codecs.open(file_name, "r", encoding) as f:
                    model_str = f.read()
            # model not present (from global repo) -> load it
            model = self._parser_blueprint.clone().get_model_from_str(
                model_str,
                file_name,
                debug=debug,
                encoding=encoding,
                pre_ref_resolution_callback=kwargs_callback,
                is_main_model=is_main_model,
            )

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
        self._obj_processors = dict(self._default_obj_processors)
        self._obj_processors.update(obj_processors)

    @property
    def _tx_model_param_definitions(self):
        warnings.warn(  # noqa: B028
            "_tx_model_param_definitions is deprecated in favor of model_param_defs."
        )
        return self.model_param_defs


class TextXMetaMetaModel:
    """
    A basic TextX meta-meta-model class that represents the meta-model of the
    textX meta-language.  Used to treat all languages in a consistent way.
    """

    def __init__(self):
        self._metamodel = None
        self.model_param_defs = ModelParamDefinitions()

    @property
    def metamodel(self):
        if self._metamodel is None:
            self._metamodel = metamodel_from_file(
                join(abspath(dirname(__file__)), "textx.tx")
            )
        return self._metamodel

    def model_from_str(self, model_str, debug=None, **kwargs):
        """
        Instantiates meta-model (a.k.a. textX model) from the given string.
        """
        return metamodel_from_str(model_str, debug=debug, **kwargs)

    def model_from_file(self, file_name, encoding="utf-8", debug=None, **kwargs):
        """
        Instantiates meta-model (a.k.a. textX model) from the given file.
        """
        return metamodel_from_file(file_name, debug=debug, **kwargs)

    def grammar_model_from_str(self, model_str, debug=None, **kwargs):
        """
        Instantiates textX grammar model from the given string.  Used to
        programmatically inspect textX grammar.
        """
        return self.metamodel.model_from_str(model_str, debug=debug, **kwargs)

    def grammar_model_from_file(self, file_name, encoding="utf-8", debug=None, **kwargs):
        """
        Instantiates textX grammar model from the given file.  Used to
        programmatically inspect textX grammar.
        """
        return self.metamodel.model_from_file(file_name, debug=debug, **kwargs)


# Register built-in textX language. See pyproject.toml entry-points
textx = LanguageDesc(
    name="textX",
    pattern="*.tx",
    description="A meta-language for language definition",
    metamodel=lambda: TextXMetaMetaModel(),
)
