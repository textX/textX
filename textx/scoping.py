#######################################################################
# Name: scoping.py
# Purpose: Meta-model / Model scoping support functions.
# Author: Pierre Bayerl
# License: MIT License
#######################################################################

from os.path import dirname,abspath
import glob,os,errno
from textx.exceptions import TextXSemanticError

"""
This module defines scope providers to be used in conjunctions with a textx.metamodel meta model.

Example grammar snippet:
    MyAttribute:
            ref=[MyInterface|FQN] name=ID ';'
    ;

The scope providers are python callables accepting obj,attr,obj_ref:
 * parser  : the current parser
 * obj     : the object representing the start of the search (e.g., a rule (e.g. "MyAttribute" in the example above, or the model)
 * attr    : a reference to the attribute "ref"
 * obj_ref : a textx.model.ObjCrossRef - the reference to be resolved

The scope provides return the referenced object (e.g. a "MyInterface" object in the example above 
(or None if nothing is found).

The scope provides are registered to the metamodel:
 * e.g., my_meta_model.register_scope_provider({"*.*":scoping.scope_provider_fully_qualified_names})
 * or: my_meta_model.register_scope_provider({"MyAttribute.ref":scoping.scope_provider_fully_qualified_names})
 * or: my_meta_model.register_scope_provider({"*.ref":scoping.scope_provider_fully_qualified_names})
 * or: my_meta_model.register_scope_provider({"MyAttribute.*":scoping.scope_provider_fully_qualified_names})

Scope providers shall be stateless or have unmodifiable state after construction: this means they should 
allow to be reused for different models (created using the same meta model) without interacting with each other.
This means, they must save their state in the corresponding model, if they need to store data (e.g., if
they load additional models from files *during name resolution*, they are not allowed to store them inside
the scope provider. Note: scope providers as normal functions (def <name>(...):..., not accessing global 
data, are safe per se.

We provide some standard scope providers:
 * scope_provider_plain_names: This is the default provider of textX.
 * scope_provider_fully_qualified_names: This is a provider similar to Java or Xtext name loopup.
 * ScopeProviderWithImportURI: This a provider which allows to load additional modules for lookup. 
   You need to define a rule with an attribute "importURI" as string (like in Xtext). This string is then used
   to load other models. Moreover, you need to provide another scope provider to manage the concrete lookup,
   e.g., the scope_provider_plain_names or the scope_provider_fully_qualified_names.
  * ScopeProviderFullyQualifiedNamesWithImportURI (decorated scope provider)
  * ScopeProviderPlainNamesWithImportURI (decorated scope provider)
 * ScopeProviderWithGlobalRepo: This is a provider where you initially need to specifiy the model files 
   to be loaded and used for lookup. Like for ScopeProviderWithImportURI you need to provide another scope 
   provider for the constere loopup. 
  * ScopeProviderFullyQualifiedNamesWithGlobalRepo (decorated scope provider)
  * ScopeProviderPlainNamesWithGlobalRepo (decorated scope provider)
"""

# -------------------------------------------------------------------------------------
# Scope helper classes:
# -------------------------------------------------------------------------------------


class Postponed:
    """
    return an object of this class to postpone a reference resolution.
    If you get circular dependencies in resolution logic, an error
    is raised.
    """
    def __init__(self):
        pass


class ModelRepository:
    """
    This class has the responsibility to
    hold a set of (model-identifiers, model) pairs
    as dictionary.
    In case of some scoping providers the model-identifier
    is the absolute filename of the model.
    """
    def __init__(self):
        self.filename_to_model={}
    def has_model(self, filename):
        return filename in self.filename_to_model.keys()


class GlobalModelRepository:
    """
    This class has the responsability to
    hold two ModelRepository objects:
    - one for model-local visible models
    - one for all models (globally, starting from
      some root model).
    The second ModelRepository "all_models" is to cache already
    loaded models and to prevent to load one model
    twice.

    The class allows loading local models visible to
    the current model. The current model is the model
    which references this GlobalModelRepository as
    attribute _tx_model_repository

    When loading a new local model, the current
    GlobalModelRepository forwards the embedded ModelRepository
    "all_models" to the new GlobalModelRepository of the
    next model. This is done using the pre_ref_resolution_callback
    to set the neccesary information before resolving
    the references in the new loaded model.
    """
    def __init__(self, all_models=None):
        """
        create a new repo for a model
        :param model the model to be added to
        :param global_repo: the repo of another (parent) model
        """
        self.local_models = ModelRepository() # used for current model
        if all_models:
            self.all_models = all_models;     # used to reuse already loaded models
        else:
            self.all_models = ModelRepository()

    def load_models_using_filepattern(self, filename_pattern, model):
        """
        add a new model to all releveant objects
        :param filename: the new model source
        :return: nothing
        """
        from textx.model import metamodel
        assert model
        self.update_model_in_repo_based_on_filename(model)
        filenames = glob.glob(filename_pattern, recursive=True)
        if len(filenames)==0:
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), filename_pattern)
        for filename in filenames:
            self.load_model(metamodel(model), filename)

    def load_model(self, themetamodel, filename):
        """
        load a single model
        :param filename: the new model source
        :return: the model
        """
        if not self.local_models.has_model(filename):
            if self.all_models.has_model(filename):
                newmodel = self.all_models.filename_to_model[filename]
            else:
                #print("LOADING {}".format(filename))
                #all models loaded here get their references resolved from the root model
                newmodel = themetamodel.internal_model_from_file(filename,
                                                        pre_ref_resolution_callback=lambda other_model:self.pre_ref_resolution_callback(other_model),
                                                                 is_this_the_main_model=False)
                self.all_models.filename_to_model[filename] = newmodel
            self.local_models.filename_to_model[filename] = newmodel
        return self.local_models.filename_to_model[filename]

    def update_model_in_repo_based_on_filename(self, model):
        from textx.model import metamodel
        assert (model._tx_model_repository == self)  # makes only sense if the correct model is used
        myfilename = model._tx_filename
        if (myfilename and (not self.all_models.has_model(myfilename))):
            # make current model visible
            # print("INIT {}".format(myfilename))
            self.all_models.filename_to_model[myfilename] = model

    def pre_ref_resolution_callback(self,other_model):
        #print("PRE-CALLBACK{}".format(filename))
        filename = other_model._tx_filename
        assert (filename)
        other_model._tx_model_repository=GlobalModelRepository(self.all_models)
        self.all_models.filename_to_model[filename] = other_model


class ModelLoader:
    """
    This class is an interface to mark a scope provider as an additional model loader.
    Such a scope provider is called
    """
    def __init__(self):
        pass

    def load_models(self, model):
        pass


def get_all_models_including_attached_models(model):
    if (hasattr(model, "_tx_model_repository")):
        models = list(model._tx_model_repository.all_models.filename_to_model.values())
        if not model in models:
            models.append(model)
    else:
        models = [model]
    return models;

# -------------------------------------------------------------------------------------
# Scope providers:
# -------------------------------------------------------------------------------------


def scope_provider_plain_names(parser, obj, attr, obj_ref):
    """
    the default scope provider
    :param parser: the current parser
    :param obj: usuned
    :param attr: unused
    :param obj_ref: the cross reference to be resolved
    """
    from textx.const import RULE_COMMON, RULE_ABSTRACT
    from textx.model import ObjCrossRef

    if obj_ref is None:
        return None # this is an error (see model.py: resolve_refs (TODO check)

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
            # allow to know the current attribute (model location for namespace)
            # and to navigate through the whole model...
            # OR (with another scope provider) to make custom lookups in the model
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

    # As a fall-back search builtins if given
    metamodel = obj._tx_metamodel
    if metamodel.builtins:
        if obj_ref.obj_name in metamodel.builtins:
            # TODO: Classes must match
            return metamodel.builtins[obj_ref.obj_name]

    return None # error handled outside


def scope_provider_fully_qualified_names(parser,obj,attr,obj_ref):
    """
    find a fully qualified name.
    Use this callable as scope_provider in a meta-model:
      my_metamodel.register_scope_provider({"*.*":scoping.scope_provider_fully_qualified_names})
    :param parser: the current parser (unused)
    :obj object corresponding a instance of an object (rule instance)
    :attr the referencing attribute (unused)
    :param obj_ref: ObjCrossRef to be resolved
    :returns None or the referenced object
    """
    def _find_obj_fqn(p, fqn_name):
        """
        Helper function:
        find a named object based on a qualified name ("."-separated names) starting from object p.
        :param p: the container where to start the search
        :param fqn_name: the "."-separated name
        :return: the object or None
        """
        def find_obj(parent, name):
            for attr in [a for a in dir(parent) if not a.startswith('__')
                                                   and not a.startswith('_tx_')
                                                   and not callable(getattr(parent, a))]:
                obj = getattr(parent, attr)
                if isinstance(obj, (list, tuple)):
                    for innerobj in obj:
                        if "name" in dir(innerobj) and innerobj.name == name: return innerobj;
                else:
                    if "name" in dir(obj) and obj.name == name: return obj;
            return None

        for n in str.split(fqn_name, '.'):
            obj = find_obj(p, n)
            if obj:
                p = obj;
            else:
                return None;
        return p;
    def _find_referenced_obj(p, name):
        """
        Helper function:
        Search the fully qualified name starting at relative container p.
        If no result is found, the search is continued from p.parent until the model root is reached.
        :param m: parent object
        :param n: name to be found
        :return: None or the found object
        """
        ret = _find_obj_fqn(p, name)
        if ret: return ret;
        while hasattr(p, "parent"):
            p = p.parent
            ret = _find_obj_fqn(p, name)
            if ret: return ret;
        return None

    from textx.model import ObjCrossRef
    assert type(obj_ref) is ObjCrossRef, type(obj_ref)
    cls, obj_name = obj_ref.cls, obj_ref.obj_name
    ret = _find_referenced_obj(obj, obj_name)
    if ret: return ret

    # As a fall-back search builtins if given
    metamodel = obj._tx_metamodel
    if metamodel.builtins:
        if obj_ref.obj_name in metamodel.builtins:
            # TODO: Classes must match
            return metamodel.builtins[obj_ref.obj_name]
    return None


class ScopeProviderWithImportURI(ModelLoader):
    """
    Scope provider like scope_provider_fully_qualified_names, but supporting Xtext-like
    importURI attributes (w/o URInamespace)

    This class requried a "simple" scope provider, which is called internally.
    """
    def __init__(self, scope_provider):
        ModelLoader.__init__(self)
        self.scope_provider = scope_provider

    def _load_referenced_models(self, model):
        from textx.model import children
        visited=[]
        for obj in children(lambda x:hasattr(x,"importURI") and not x in visited,model):
            visited.append(obj)
            # TODO add multiple lookup rules for file search
            filename_pattern = abspath(dirname(model._tx_filename)+"/"+obj.importURI)
            model._tx_model_repository.load_models_using_filepattern(filename_pattern, model=model)

    def load_models(self, model):
        from textx.model import metamodel
        # do we already have loaded models (analysis)? No -> check/load them
        if "_tx_model_repository" in dir(model):
            pass
        else:
            if "_tx_model_repository" in dir(metamodel(model)):
                model_repository = GlobalModelRepository(metamodel(model._tx_model_repository.all_models))
            else:
                model_repository = GlobalModelRepository()
            model._tx_model_repository = model_repository
        self._load_referenced_models(model)


    def __call__(self, parser, obj, attr, obj_ref):
        from textx.model import ObjCrossRef, model_root
        assert type(obj_ref) is ObjCrossRef, type(obj_ref)
        #cls, obj_name = obj_ref.cls, obj_ref.obj_name

        # 1) lookup URIs... (first, before looking locally - to detect file not founds and distant model errors...)
        # TODO: raise error if lookup is not unique

        model = model_root(obj)
        model_repository = model._tx_model_repository

        # 1) try to find object locally
        ret = self.scope_provider(parser, obj, attr, obj_ref)
        if ret: return ret

        # 2) do we have loaded models?
        for m in model_repository.local_models.filename_to_model.values():
            ret = self.scope_provider(parser, m, attr, obj_ref)
            if ret: return ret
        return None


class ScopeProviderFullyQualifiedNamesWithImportURI(ScopeProviderWithImportURI):
    def __init__(self):
        ScopeProviderWithImportURI.__init__(self, scope_provider_fully_qualified_names)


class ScopeProviderPlainNamesWithImportURI(ScopeProviderWithImportURI):
    def __init__(self):
        ScopeProviderWithImportURI.__init__(self, scope_provider_plain_names)


class ScopeProviderWithGlobalRepo(ScopeProviderWithImportURI):
    """
    Scope provider that allows to populate the set of models used for lookup before parsing models.
    Usage:
      * create metamodel
      * create ScopeProviderFullyQualifiedNamesWithGlobalRepo
      * register models used for lookup into the scope provider
    Then the scope provider is ready to be registered and used.
    """
    def __init__(self, scope_provider, filename_pattern=None):
        ScopeProviderWithImportURI.__init__(self, scope_provider)
        self.filename_pattern_list=[]
        if filename_pattern: self.register_models(filename_pattern)

    def register_models(self, filename_pattern):
        """
        register models into provider object - visible for all
        :param mymetamodel: the metamodel to be used to load the models
        :param filename_pattern: the pattern (e.g. file.myext or dir/**/*.myext)
        :return: nothing
        """
        self.filename_pattern_list.append(filename_pattern)

    def _load_referenced_models(self, model):
        for filename_pattern in self.filename_pattern_list:
            model._tx_model_repository.load_models_using_filepattern(filename_pattern, model=model)


class ScopeProviderFullyQualifiedNamesWithGlobalRepo(ScopeProviderWithGlobalRepo):
    def __init__(self,filename_pattern=None):
        ScopeProviderWithGlobalRepo.__init__(self, scope_provider_fully_qualified_names, filename_pattern)


class ScopeProviderPlainNamesWithGlobalRepo(ScopeProviderWithGlobalRepo):
    def __init__(self, filename_pattern=None):
        ScopeProviderWithGlobalRepo.__init__(self, scope_provider_plain_names, filename_pattern)

# --------------------------------------


def find_named_and_typed_object_in_list(obj, field_name, desired_type, name):
    if type(obj) is Postponed: return obj
    lst = getattr(obj, field_name)
    assert type(lst) is list
    for res in lst:
        if "name" in dir(res) and getattr(res,"name")==name:
            if isinstance(res, desired_type):
                return res
            else:
                raise TypeError("{} has type {} instead of {}.".format(name,type(res).__name__, desired_type.__name__))
    return None #not found


def get_referenced_object(obj, dot_separated_name):
    names = dot_separated_name.split(".")
    next_obj = getattr(obj, names[0])
    if not next_obj: return Postponed()
    if len(names)>1:
        return get_referenced_object(next_obj,".".join(names[1:]))
    return next_obj


#TODO: optional "inheritance" (with/without inheritance) may be difficult to distinguish from unresolved (--> postponed)
#maybe via lambdas + user logic...
class ScopeProviderForSimpleRelativeNamedLookups:
    def __init__(self,path_to_conatiner_object,name_of_list_of_named_objects):
        self.path_to_conatiner_object = path_to_conatiner_object
        self.name_of_list_of_named_objects = name_of_list_of_named_objects
        self.postponed_counter=0;

    def __call__(self, parser, obj, attr, obj_ref):
        try:
            res = find_named_and_typed_object_in_list(get_referenced_object(obj, self.path_to_conatiner_object),
                                                       self.name_of_list_of_named_objects,
                                                       obj_ref.cls,
                                                       obj_ref.obj_name)
            if type(res) is Postponed:
                self.postponed_counter+=1;
            return res
        except TypeError as e:
            line, col = parser.pos_to_linecol(obj_ref.position)
            raise TextXSemanticError('{}'.format(str(e)), line=line, col=col)
