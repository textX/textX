#######################################################################
# Name: scoping.providers.py
# Purpose: Meta-model / scope providers.
# Author: Pierre Bayerl
# License: MIT License
#######################################################################

from os.path import dirname, abspath
from textx.exceptions import TextXSemanticError
import textx.scoping as scoping

"""
This module defines scope providers to be used in conjunctions with a 
textx.metamodel meta model.

See docs/scoping.md

"""


class PlainName(object):
    """
    plain name scope provider
    """

    def __init__(self):
        pass;

    def __call__(self, parser, obj, attr, obj_ref):
        """
        the default scope provider

        Args:
            parser: the current parser
            obj: unused
            attr: unused
            obj_ref: the cross reference to be resolved

        Returns:
            the resolved reference or None
        """
        from textx.const import RULE_COMMON, RULE_ABSTRACT
        from textx.model import ObjCrossRef

        if obj_ref is None:
            return None  # an error! (see model.py: resolve_refs (TODO check)

        assert type(obj_ref) is ObjCrossRef, type(obj_ref)

        if parser.debug:
            parser.dprint("Resolving obj crossref: {}:{}"
                          .format(obj_ref.cls, obj_ref.obj_name))
        print("Resolving obj crossref: {}:{}"
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
                if id(cls) in parser._instances:
                    objs = parser._instances[id(cls)]
                    if obj_name in objs:
                        return objs[obj_name]

        result = _inner_resolve_link_rule_ref(obj_ref.cls,
                                              obj_ref.obj_name)
        if result:
            return result

        return None  # error handled outside


class FQN(object):
    """
    fully qualified name scope provider
    """

    def __init__(self):
        pass;

    def __call__(self, parser, obj, attr, obj_ref):
        """
        find a fully qualified name.
        Use this callable as scope_provider in a meta-model:
          my_metamodel.register_scope_provider(
            {"*.*":textx.scoping.providers.FQN})
        :param parser: the current parser (unused)
        :obj object corresponding a instance of an object (rule instance)
        :attr the referencing attribute (unused)
        :param obj_ref: ObjCrossRef to be resolved
        :returns None or the referenced object
        """

        def _find_obj_fqn(p, fqn_name):
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
                for attr in [a for a in parent.__dict__ if
                             not a.startswith('__') and not
                             a.startswith('_tx_') and not
                             callable(getattr(parent, a))]:
                    obj = getattr(parent, attr)
                    if isinstance(obj, (list, tuple)):
                        for innerobj in obj:
                            if hasattr(innerobj, "name") \
                                    and innerobj.name == name:
                                return innerobj
                    else:
                        if hasattr(obj, "name") and obj.name == name:
                            return obj
                return None

            for n in fqn_name.split('.'):
                obj = find_obj(p, n)
                if obj:
                    p = obj
                else:
                    return None
            return p

        def _find_referenced_obj(p, name):
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
            ret = _find_obj_fqn(p, name)
            if ret:
                return ret
            while hasattr(p, "parent"):
                p = p.parent
                ret = _find_obj_fqn(p, name)
                if ret:
                    return ret
            return None

        from textx.model import ObjCrossRef
        assert type(obj_ref) is ObjCrossRef, type(obj_ref)
        cls, obj_name = obj_ref.cls, obj_ref.obj_name
        ret = _find_referenced_obj(obj, obj_name)
        if ret:
            return ret
        else:
            return None


class ImportURI(scoping.ModelLoader):
    """
    Scope provider supporting Xtext-like importURI attributes (w/o
    URInamespace). This class requries another scope provider, which is
    called internally.
    """

    def __init__(self, scope_provider, glob_args=None):
        from textx.scoping import ModelLoader
        ModelLoader.__init__(self)
        self.scope_provider = scope_provider
        self.glob_args = {}
        if glob_args:
            self.set_glob_args(glob_args)

    def set_glob_args(self, glob_args):
        self.glob_args = glob_args

    def _load_referenced_models(self, model):
        from textx.model import get_children
        visited = []
        for obj in get_children(
                lambda x: hasattr(x, "importURI") and x not in visited, model):
            visited.append(obj)
            # TODO add multiple lookup rules for file search
            basedir = dirname(model._tx_filename)
            if len(basedir) > 0:
                basedir += "/"
            filename_pattern = abspath(basedir + obj.importURI)
            model._tx_model_repository.load_models_using_filepattern(
                filename_pattern, model=model, glob_args=self.glob_args)

    def load_models(self, model):
        from textx.model import get_metamodel
        from textx.scoping import GlobalModelRepository
        # do we already have loaded models (analysis)? No -> check/load them
        if hasattr(model, "_tx_model_repository"):
            pass
        else:
            if hasattr(get_metamodel(model), "_tx_model_repository"):
                model_repository = GlobalModelRepository(get_metamodel(
                    model._tx_model_repository.all_models))
            else:
                model_repository = GlobalModelRepository()
            model._tx_model_repository = model_repository
        self._load_referenced_models(model)

    def __call__(self, parser, obj, attr, obj_ref):
        from textx.model import ObjCrossRef, get_model
        assert type(obj_ref) is ObjCrossRef, type(obj_ref)
        # cls, obj_name = obj_ref.cls, obj_ref.obj_name

        # 1) lookup URIs... (first, before looking locally - to detect file
        #    not founds and distant model errors...)
        # TODO: raise error if lookup is not unique

        model = get_model(obj)
        model_repository = model._tx_model_repository

        # 1) try to find object locally
        ret = self.scope_provider(parser, obj, attr, obj_ref)
        if ret:
            return ret

        # 2) do we have loaded models?
        for m in model_repository.local_models.filename_to_model.values():
            ret = self.scope_provider(parser, m, attr, obj_ref)
            if ret:
                return ret
        return None


class FQNImportURI(ImportURI):
    """
    scope provider with ImportURI and FQN
    """

    def __init__(self, glob_args=None):
        ImportURI.__init__(self, FQN(), glob_args=glob_args)


class PlainNameImportURI(ImportURI):
    """
    scope provider with ImportURI and PlainName names
    """

    def __init__(self, glob_args=None):
        ImportURI.__init__(self, PlainName(), glob_args=glob_args)


class GlobalRepo(ImportURI):
    """
    Scope provider that allows to populate the set of models used for lookup
    before parsing models.

    Usage:
      * create metamodel
      * create FQNGlobalRepo
      * register models used for lookup into the scope provider
    Then the scope provider is ready to be registered and used.
    """

    def __init__(self, scope_provider, filename_pattern=None, glob_args=None):
        ImportURI.__init__(self, scope_provider, glob_args=glob_args)
        self.filename_pattern_list = []
        if filename_pattern:
            self.register_models(filename_pattern)

    def register_models(self, filename_pattern):
        """
        register models into provider object - visible for all

        Args:
            mymetamodel: the metamodel to be used to load the models
            filename_pattern: the pattern (e.g. file.myext or dir/**/*.myext)

        Returns:
            nothing
        """
        self.filename_pattern_list.append(filename_pattern)

    def _load_referenced_models(self, model):
        for filename_pattern in self.filename_pattern_list:
            model._tx_model_repository.load_models_using_filepattern(
                filename_pattern, model=model, glob_args=self.glob_args)


class FQNGlobalRepo(GlobalRepo):
    """
    scope provider with FQN and global repo
    """

    def __init__(self, filename_pattern=None, glob_args=None):
        GlobalRepo.__init__(self, FQN(), filename_pattern,
                            glob_args=glob_args)


class PlainNameGlobalRepo(GlobalRepo):
    """
    scope provider with PlainName names and global repo
    """

    def __init__(self, filename_pattern=None, glob_args=None):
        GlobalRepo.__init__(
            self, PlainName(), filename_pattern, glob_args=glob_args)


class RelativeName(object):
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

    def __call__(self, parser, obj, attr, obj_ref):
        from textx.scoping.tools import get_referenced_object
        from textx.scoping import Postponed
        try:
            res = get_referenced_object(
                None, obj,
                self.path_to_container_object + "." + obj_ref.obj_name,
                parser, obj_ref.cls)
            if type(res) is Postponed:
                self.postponed_counter += 1
            return res
        except TypeError as e:
            line, col = parser.pos_to_linecol(obj_ref.position)
            raise TextXSemanticError('{}'.format(str(e)), line=line, col=col)


class ExtRelativeName(object):
    """
    Similar as RelativeName.
    Here you specifiy separately
    - how to find the class.
    - how to find the methods (starting from a class).
    - how to find inherited/chained classes (starting from a class).
    """

    def __init__(self, path_to_definition_object, path_to_target,
                 path_to_extension):
        self.path_to_definition_object = path_to_definition_object
        self.path_to_target = path_to_target
        self.path_to_extension = path_to_extension
        self.postponed_counter = 0

    def __call__(self, parser, obj, attr, obj_ref):
        from textx.scoping.tools import get_referenced_object, \
            get_list_of_concatenated_objects
        from textx.scoping import Postponed
        try:
            one_def_obj = get_referenced_object(
                None, obj, self.path_to_definition_object, parser)
            def_obj_list = get_list_of_concatenated_objects(
                one_def_obj, self.path_to_extension, parser, [])
            for def_obj in def_obj_list:
                if type(def_obj) is Postponed:
                    self.postponed_counter += 1
                    return def_obj
                res = get_referenced_object(
                    None, def_obj,
                    self.path_to_target + "." + obj_ref.obj_name, parser,
                    obj_ref.cls)
                if res:
                    return res  # may be Postponed
            return None
        except TypeError as e:
            line, col = parser.pos_to_linecol(obj_ref.position)
            raise TextXSemanticError(
                'ExtRelativeName: {}'.format(str(e)), line=line, col=col)
