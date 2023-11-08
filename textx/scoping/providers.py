#######################################################################
# Name: scoping.providers.py
# Purpose: Meta-model / scope providers.
# Author: Pierre Bayerl
# License: MIT License
#######################################################################

from os.path import abspath, dirname, isabs, join

import textx.scoping as scoping
from textx.exceptions import TextXSemanticError
from textx.scoping import Postponed

"""
This module defines scope providers to be used in conjunctions with a
textx.metamodel meta model.

See docs/scoping.md

"""


class PlainName:
    """
    plain name scope provider
    """

    def __init__(self, multi_metamodel_support=True):
        """
        the default scope provider constructor

        Args:
            multi_metamodel_support: enable a AST based search, instead
            of using the parser._instances
        """
        self.multi_metamodel_support = multi_metamodel_support
        pass

    def __call__(self, obj, attr, obj_ref):
        """
        the default scope provider

        Args:
            obj: unused (used for multi_metamodel_support)
            attr: unused
            obj_ref: the cross reference to be resolved

        Returns:
            the resolved reference or None
        """
        from textx.const import RULE_ABSTRACT, RULE_COMMON
        from textx.model import ObjCrossRef
        from textx.scoping.tools import get_parser

        if obj_ref is None:
            return None  # an error! (see model.py: resolve_refs (TODO check)

        assert type(obj_ref) is ObjCrossRef, type(obj_ref)

        if get_parser(obj).debug:
            get_parser(obj).dprint(
                f"Resolving obj crossref: {obj_ref.cls}:{obj_ref.obj_name}"
            )

        def _inner_resolve_link_rule_ref(cls, obj_name):
            """
            Depth-first resolving of link rule reference.
            """
            if cls._tx_type is RULE_ABSTRACT:
                for inherited in cls._tx_inh_by:
                    result = _inner_resolve_link_rule_ref(inherited, obj_name)
                    if result:
                        return result
            elif cls._tx_type == RULE_COMMON and id(cls) in get_parser(obj)._instances:
                # TODO make this code exchangable
                # allow to know the current attribute (model location for
                # namespace) and to navigate through the whole model...
                # OR (with another scope provider) to make custom lookups in
                # the model
                #
                # Scopeprovider
                # - needs: .current reference (in the model)
                #          .the model (?)
                # - provides: the resolved object or None
                objs = get_parser(obj)._instances[id(cls)]
                return objs.get(obj_name)

        if self.multi_metamodel_support:
            from textx import get_children, get_model, textx_isinstance

            result_lst = get_children(
                lambda x: hasattr(x, "name")
                and x.name == obj_ref.obj_name
                and textx_isinstance(x, obj_ref.cls),
                get_model(obj),
            )
            if len(result_lst) == 1:
                result = result_lst[0]
            elif len(result_lst) > 1:
                line, col = get_parser(obj).pos_to_linecol(obj_ref.position)
                raise TextXSemanticError(
                    f"name {obj_ref.obj_name} is not unique.",
                    line=line,
                    col=col,
                    filename=get_model(obj)._tx_filename,
                )
            else:
                result = None
        else:
            result = _inner_resolve_link_rule_ref(obj_ref.cls, obj_ref.obj_name)
        return result  # error handled outside


class FQN:
    """
    fully qualified name scope provider
    """

    def __init__(self, scope_redirection_logic=None):
        """
        Args:
            scope_redirection_logic: this callable gets a
            named model being processed. **(a)** This callable
            is required to return a list of elements,
            in which the FQN provider continues to
            search for named elements (you may also
            return an empty list of a list with one
            element). **(b)** The scope_redirection_logic may
            also return a Postponed object. **(c)** The
            scope_redirection_logic is not applied for the
            object containing the reference to be resolved
            (in order to prevent getting circular dependencies).
        """
        self.scope_redirection_logic = scope_redirection_logic

    def __call__(self, current_obj, attr, obj_ref):
        """
        find a fully qualified name.
        Use this callable as scope_provider in a meta-model:
          my_metamodel.register_scope_provider(
            {"*.*":textx.scoping.providers.FQN})

        Args:
            current_obj: object corresponding a instance of an
                         object (rule instance)
            attr: the referencing attribute (unused)
            obj_ref: ObjCrossRef to be resolved

        Returns: None or the referenced object
        """

        def _find_obj_fqn(p, fqn_name, cls):
            """
            Helper function:
            find a named object based on a qualified name ("."-separated
            names) starting from object p.

            Args:
                p: the container where to start the search
                fqn_name: the "."-separated name

            Returns:
                the object or None
            """

            def find_obj(parent, name):
                if parent is not current_obj and self.scope_redirection_logic is not None:
                    from textx.scoping import Postponed

                    res = self.scope_redirection_logic(parent)
                    assert res is not None, "scope_redirection_logic must not return None"
                    if type(res) is Postponed:
                        return res
                    for m in res:
                        return_value = find_obj(m, name)
                        if return_value is not None:
                            return return_value
                for attr in [
                    a
                    for a in parent.__dict__
                    if not a.startswith("__")
                    and not a.startswith("_tx_")
                    and not callable(getattr(parent, a))
                ]:
                    obj = getattr(parent, attr)
                    if isinstance(obj, (list, tuple)):
                        for innerobj in obj:
                            if hasattr(innerobj, "name") and innerobj.name == name:
                                return innerobj
                    else:
                        if hasattr(obj, "name") and obj.name == name:
                            return obj
                return None

            for n in fqn_name.split("."):
                obj = find_obj(p, n)
                if obj is not None:
                    if type(obj) is Postponed:
                        return obj
                    p = obj
                else:
                    return None

            from textx import textx_isinstance

            if textx_isinstance(obj, cls):
                return p
            else:
                return None

        def _find_referenced_obj(p, name, cls):
            """
            Helper function:
            Search the fully qualified name starting at relative container p.
            If no result is found, the search is continued from p.parent until
            the model root is reached.

            Args:
                p: parent object
                name: name to be found

            Returns:
                None or the found object
            """
            ret = _find_obj_fqn(p, name, cls)
            if ret:
                return ret
            while hasattr(p, "parent"):
                p = p.parent
                ret = _find_obj_fqn(p, name, cls)
                if ret:
                    return ret
                # else continue to next parent or return None

        from textx.model import ObjCrossRef

        assert type(obj_ref) is ObjCrossRef, type(obj_ref)
        obj_cls, obj_name = obj_ref.cls, obj_ref.obj_name
        return _find_referenced_obj(current_obj, obj_name, obj_cls)


class ImportURI(scoping.ModelLoader):
    """
    Scope provider supporting Xtext-like importURI attributes (w/o
    URInamespace). This class requires another scope provider, which is
    called internally.

    Adds the loaded models to the importURI-objects: Thus, a model element
    used to import another model references all loaded models with this
    command in an attribute _tx_loaded_models (list of models).

    If "importAs" is enabled AND the rule with the "importURI" attribute
    has a "name" not None or an empty String, the loaded model is not
    added to the list of globally visible models..

    The importURI_converter is used to process the importURI attribute to
    yield a filename or a filename pattern.
    """

    def __init__(
        self,
        scope_provider,
        glob_args=None,
        search_path=None,
        importAs=False,
        importURI_converter=None,
        importURI_to_scope_name=None,
    ):
        """
        Creates a new ImportURI Provider.
        Args:
            scope_provider: The underlying scope provider to be used to locate
                mode items
            glob_args: arguments for the glob module (you can load model
                elements using globbing. With this arg you can enable, e.g.,
                recursion while globbing. This option is irrelevant when
                using a search path.
            search_path: a list with path strings used to find files. Without
                this information (None), the current model file location
                indicates where to search files.
            importAs: activate importAs feature (see class documentation).
            importURI_converter: Callable to convert the importURI attribute
                to a filename pattern (default: None).
            importURI_to_scope_name: Callable to define a name based on the
                rule instance containing the importURI attribute. With this
                you can set the name of the importURI object to something
                dependent of the original importURI value (caution: for an
                FQN based lookup, this name should NOT contain dots '.').

        """
        from textx.scoping import ModelLoader

        ModelLoader.__init__(self)
        self.scope_provider = scope_provider
        if (glob_args is not None) and (search_path is not None):
            raise Exception("you cannot use globbing together with a " "search path")
        self.glob_args = {}
        self.search_path = search_path
        self.importAs = importAs
        if importURI_converter is not None:
            self.importURI_converter = importURI_converter
        else:
            self.importURI_converter = lambda x: x
        self.importURI_to_scope_name = importURI_to_scope_name
        if glob_args:
            self.set_glob_args(glob_args)

    def set_glob_args(self, glob_args):
        self.glob_args = glob_args

    def _load_referenced_models(self, model, encoding):
        from textx.model import get_children

        visited = []
        for obj in get_children(
            lambda x: hasattr(x, "importURI") and x not in visited, model
        ):
            add_to_local_models = True
            if self.importURI_to_scope_name is not None:
                obj.name = self.importURI_to_scope_name(obj)
                # print("setting name to {}".format(obj.name))
            if hasattr(obj, "name") and obj.name is not None and obj.name != "":
                add_to_local_models = not self.importAs

            visited.append(obj)
            if self.search_path is not None:
                # search_path based i/o:
                my_search_path = [dirname(model._tx_filename)] + self.search_path
                loaded_model = model._tx_model_repository.load_model_using_search_path(
                    self.importURI_converter(obj.importURI),
                    model=model,
                    search_path=my_search_path,
                    encoding=encoding,
                    add_to_local_models=add_to_local_models,
                    model_params=model._tx_model_params,
                )
                obj._tx_loaded_models = [loaded_model]

            else:
                # globing based i/o:
                basedir = dirname(model._tx_filename)
                filename_pattern = abspath(
                    join(basedir, self.importURI_converter(obj.importURI))
                )

                obj._tx_loaded_models = (
                    model._tx_model_repository.load_models_using_filepattern(
                        filename_pattern,
                        model=model,
                        glob_args=self.glob_args,
                        encoding=encoding,
                        add_to_local_models=add_to_local_models,
                        model_params=model._tx_model_params,
                    )
                )

    def load_models(self, model, encoding="utf-8"):
        from textx.model import get_metamodel
        from textx.scoping import GlobalModelRepository

        # do we already have loaded models (analysis)? No -> check/load them
        if hasattr(model, "_tx_model_repository"):
            pass
        else:
            if hasattr(get_metamodel(model), "_tx_model_repository"):
                model_repository = GlobalModelRepository(
                    get_metamodel(model)._tx_model_repository.all_models
                )
            else:
                model_repository = GlobalModelRepository()
            model._tx_model_repository = model_repository
        self._load_referenced_models(model, encoding=encoding)

    def __call__(self, obj, attr, obj_ref):
        from textx.model import ObjCrossRef, get_model

        assert type(obj_ref) is ObjCrossRef, type(obj_ref)
        # cls, obj_name = obj_ref.cls, obj_ref.obj_name

        # 1) lookup URIs... (first, before looking locally - to detect file
        #    not founds and distant model errors...)
        # TODO: raise error if lookup is not unique

        model = get_model(obj)
        model_repository = model._tx_model_repository

        # 1) try to find object locally
        ret = self.scope_provider(obj, attr, obj_ref)
        if ret:
            return ret

        # 2) do we have loaded models?
        for m in model_repository.local_models:
            ret = self.scope_provider(m, attr, obj_ref)
            if ret:
                return ret

        # 3) Use builtin models as a fallback if provided
        if model._tx_metamodel.builtin_models:
            for m in model._tx_metamodel.builtin_models:
                ret = self.scope_provider(m, attr, obj_ref)
                if ret:
                    return ret
        return None


def follow_loaded_models_scope_redirection_logic(obj, scope_redirection_logic):
    lst = []
    if scope_redirection_logic is not None:
        lst = scope_redirection_logic(obj)
        assert lst is not None, "scope_redirection_logic must not return None"
        if type(lst) is Postponed:
            return lst
    if hasattr(obj, "_tx_loaded_models"):
        lst = lst + obj._tx_loaded_models
    return lst


class FQNImportURI(ImportURI):
    """
    scope provider with ImportURI and FQN

    If "importAs" is enabled the FQN scope provider will
    get parameters to "bridge" over elements with _tx_loaded_models
    attributes (allowing to reference imported models through named
    importURI based rule instances).

    See also: "test_importURI_variations.py".
    """

    def __init__(
        self,
        glob_args=None,
        search_path=None,
        importAs=False,
        importURI_converter=None,
        importURI_to_scope_name=None,
        scope_redirection_logic=None,
    ):
        if importAs:

            def my_scope_redirection_logic_def(obj):
                return follow_loaded_models_scope_redirection_logic(
                    obj, scope_redirection_logic
                )

            my_scope_redirection_logic = my_scope_redirection_logic_def
        else:
            my_scope_redirection_logic = scope_redirection_logic
        ImportURI.__init__(
            self,
            FQN(scope_redirection_logic=my_scope_redirection_logic),
            glob_args=glob_args,
            search_path=search_path,
            importAs=importAs,
            importURI_converter=importURI_converter,
            importURI_to_scope_name=importURI_to_scope_name,
        )


class PlainNameImportURI(ImportURI):
    """
    scope provider with ImportURI and PlainName names
    """

    def __init__(self, glob_args=None, search_path=None, importURI_converter=None):
        ImportURI.__init__(
            self,
            PlainName(),
            glob_args=glob_args,
            search_path=search_path,
            importURI_converter=importURI_converter,
        )


class GlobalRepo(ImportURI):
    """
    Scope provider that allows to populate the set of models used for lookup
    before parsing models.

    Usage:
      * create metamodel
      * create FQNGlobalRepo
      * register models used for lookup into the scope provider
    Then the scope provider is ready to be registered and used.

    The model parameter `project_root` (see _tx_model_params) can be used to
    set a project directory, where all file patterns not referring to an
    absolute file position are looked up.
    """

    def __init__(self, scope_provider, filename_pattern=None, glob_args=None):
        ImportURI.__init__(self, scope_provider, glob_args=glob_args)
        self.filename_pattern_list = []
        self.models_to_be_added_directly = []
        if filename_pattern:
            self.register_models(filename_pattern)

    def register_models(self, filename_pattern):
        """
        register models into provider object - visible for all

        Args:
            filename_pattern: the pattern (e.g. file.myext or dir/**/*.myext)

        Returns:
            None
        """
        self.filename_pattern_list.append(filename_pattern)

    def _load_referenced_models(self, model, encoding):
        for filename_pattern in self.filename_pattern_list:
            if not isabs(filename_pattern) and "project_root" in model._tx_model_params:
                filename_pattern = join(
                    model._tx_model_params["project_root"], filename_pattern
                )
            model._tx_model_repository.load_models_using_filepattern(
                filename_pattern,
                model=model,
                glob_args=self.glob_args,
                encoding=encoding,
                model_params=model._tx_model_params,
            )
        for m in self.models_to_be_added_directly:
            model._tx_model_repository._add_model(m)

    def add_model(self, model):
        """
        Adds a model directly. Useful when combining models
        parsed from a string (instead of a file).
        Args:
            model: the model to be added later.
        """
        self.models_to_be_added_directly.append(model)

    def load_models_in_model_repo(
        self, global_model_repo=None, encoding="utf-8", **kwargs
    ):
        """
        load all registered models (called explicitly from
        the user and not as an automatic activity).
        Normally this is done automatically while
        reference resolution of one loaded model.

        However, if you wish to load all models
        you can call this and get a model repository.

        The metamodels must be identifiable via the MetaModelProvider.

        kwargs are passed (like for `model_from_str' or
        `model_from_file`, but no checks are performed.
        You have to call the check manually, if you want
        to check for undefined parameters (else, undefined
        parameters passed via kwargs here are ignored).

        Returns:
            a GlobalModelRepository with the loaded models
        """
        import textx.scoping
        from textx.model_params import ModelParams

        if not global_model_repo:
            global_model_repo = textx.scoping.GlobalModelRepository()
        for filename_pattern in self.filename_pattern_list:
            global_model_repo.load_models_using_filepattern(
                filename_pattern,
                model=None,
                glob_args=self.glob_args,
                is_main_model=True,
                encoding=encoding,
                model_params=ModelParams(kwargs),
            )
        return global_model_repo


class FQNGlobalRepo(GlobalRepo):
    """
    scope provider with FQN and global repo
    """

    def __init__(self, filename_pattern=None, glob_args=None):
        GlobalRepo.__init__(self, FQN(), filename_pattern, glob_args=glob_args)


class PlainNameGlobalRepo(GlobalRepo):
    """
    scope provider with PlainName names and global repo
    """

    def __init__(self, filename_pattern=None, glob_args=None):
        GlobalRepo.__init__(self, PlainName(), filename_pattern, glob_args=glob_args)


class RelativeName:
    """
    allows to implement a class-method-instance-like scoping:
     - define a class with methods
     - define instances
     - allow to define a scope where the instance references the methods
    Note: The same as for classes/methods can be interpreted as
    components/slots...
    """

    def __init__(self, path_to_container_object):
        """
        Here, you specify the path from the instance to the methods:
        The path is given in a dot-separated way: "classref.methods". Then a
        concrete method "f" is searched as "classref.methods.f".

        Args:
            path_to_container_object: This identifies (starting from the
            instance) how to find the methods.
        """
        self.path_to_container_object = path_to_container_object
        self.postponed_counter = 0

    def get_reference_propositions(self, obj, attr, name_part):
        """
        retrieve a list of reference propositions.
        Args:
            obj: parent
            attr: attribute
            name_part: The name is used to build the list
                (e.g. using a substring-like logic).
        Returns:
            the list of objects representing the proposed references
        """
        from textx import textx_isinstance
        from textx.scoping.tools import resolve_model_path

        obj_list = resolve_model_path(obj, self.path_to_container_object)
        if type(obj_list) is Postponed:
            self.postponed_counter += 1
            return obj_list
        # the referenced element must be a list
        # (else it is a design error in the path passed to
        # the RelativeName object).
        if not isinstance(obj_list, list):
            from textx.exceptions import TextXError

            raise TextXError(
                f"expected path to list in the model ({self.path_to_container_object})"
            )
        obj_list = filter(
            lambda x: textx_isinstance(x, attr.cls) and x.name.find(name_part) >= 0,
            obj_list,
        )

        return list(obj_list)

    def __call__(self, obj, attr, obj_ref):
        lst = self.get_reference_propositions(obj, attr, obj_ref.obj_name)
        if type(lst) is Postponed:
            return lst
        lst = [x for x in lst if x.name == obj_ref.obj_name]
        if len(lst) > 0:
            return lst[0]
        else:
            return None


class ExtRelativeName:
    """
    Similar as RelativeName.
    Here you specify separately
    - how to find the class.
    - how to find the methods (starting from a class).
    - how to find inherited/chained classes (starting from a class).
    """

    def __init__(self, path_to_definition_object, path_to_target, path_to_extension):
        self.path_to_definition_object = path_to_definition_object
        self.path_to_target = path_to_target
        self.path_to_extension = path_to_extension
        self.postponed_counter = 0

    def get_reference_propositions(self, obj, attr, name_part):
        """
        retrieve a list of reference propositions.
        Args:
            obj: parent
            attr: attribute
            name_part: The name is used to build the list
                (e.g. using a substring-like logic).
        Returns:
            the list of objects representing the proposed references
        """
        from textx import textx_isinstance

        # find all all "connected" objects
        # (e.g. find all classes: the most derived
        # class, its base, the base of its base, etc.)
        from textx.scoping.tools import (
            get_list_of_concatenated_objects,
            resolve_model_path,
        )

        def_obj = resolve_model_path(obj, self.path_to_definition_object)
        def_objs = get_list_of_concatenated_objects(def_obj, self.path_to_extension)
        # for all containing classes, collect all
        # objects to be looked up (e.g. methods)
        obj_list = []
        for def_obj in def_objs:
            if type(def_obj) is Postponed:
                self.postponed_counter += 1
                return def_obj

            tmp_list = resolve_model_path(def_obj, self.path_to_target)
            assert tmp_list is not None
            # expected to point to  alist
            if not isinstance(tmp_list, list):
                from textx.exceptions import TextXError

                raise TextXError(
                    f"expected path to list in the model ({self.path_to_target})"
                )
            tmp_list = list(
                filter(
                    lambda x: textx_isinstance(x, attr.cls)
                    and x.name.find(name_part) >= 0,
                    tmp_list,
                )
            )
            obj_list = obj_list + tmp_list

        return list(obj_list)

    def __call__(self, obj, attr, obj_ref):
        lst = self.get_reference_propositions(obj, attr, obj_ref.obj_name)
        if type(lst) is Postponed:
            return lst
        lst = [x for x in lst if x.name == obj_ref.obj_name]
        if len(lst) > 0:
            return lst[0]
        else:
            return None
